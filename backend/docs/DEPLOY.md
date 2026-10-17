# Развёртывание бэкенда (черновик на после MVP)

> Черновик. Сервер и домен ещё не выбраны (SPEC.md, раздел 9). Перед первым запуском нужно уточнить домены, почту и схему прокси с фронтендом (см. «Решения перед запуском»).

Целевая схема: VPS (Ubuntu 24.04 LTS) → nginx (HTTPS, статика, media) → gunicorn → Django. База — SQLite, файлы — `media/` на диске сервера.

```
браузер ──HTTPS──> nginx :443 ──> gunicorn (unix-сокет) ──> Django
                     ├─ /static/  → backend/staticfiles/
                     └─ /media/   → backend/media/
```

## 1. Сервер

```bash
sudo apt update && sudo apt install -y python3.12 python3.12-venv git nginx sqlite3 certbot python3-certbot-nginx
sudo adduser --system --group --home /srv/icc icc
sudo -u icc git clone https://github.com/AmirSaidov/icc-website.git /srv/icc/app
cd /srv/icc/app/backend
sudo -u icc python3.12 -m venv .venv
sudo -u icc .venv/bin/pip install -r requirements.txt gunicorn
```

## 2. `.env` на сервере

`/srv/icc/app/backend/.env`, права `600`, владелец `icc`:

```
SECRET_KEY=<50+ случайных символов: python -c "import secrets; print(secrets.token_urlsafe(50))">
DEBUG=False
ALLOWED_HOSTS=api.<домен>
CORS_ALLOWED_ORIGINS=https://<домен фронта>
CSRF_TRUSTED_ORIGINS=https://api.<домен>
ADMIN_URL=<нестандартный путь, например cpk-7f3k9q/>
FRONTEND_URL=https://<домен фронта>
BACKEND_URL=https://api.<домен>
NUM_PROXIES=1
EMAIL_HOST=<SMTP заказчика>
EMAIL_PORT=587
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@<домен>
FEEDBACK_EMAIL=<куда слать заявки, если в админке не задано>
```

При `DEBUG=False` автоматически включаются HSTS (1 год), secure-cookies, `SECURE_PROXY_SSL_HEADER`, nosniff, `X-Frame-Options: DENY`.

## 3. Подготовка базы и статики

```bash
cd /srv/icc/app/backend
sudo -u icc .venv/bin/python manage.py migrate
sudo -u icc .venv/bin/python manage.py createcachetable
sudo -u icc .venv/bin/python manage.py collectstatic --noinput
sudo -u icc .venv/bin/python manage.py createsuperuser
sudo -u icc .venv/bin/python manage.py check --deploy
```

`check --deploy` должен показать только три осознанных предупреждения: W005, W008, W021 (см. раздел 8). `seed` на сервере **не запускать**: это тестовые данные.

## 4. gunicorn (systemd)

`/etc/systemd/system/icc-backend.service`:

```ini
[Unit]
Description=ICC backend (gunicorn)
After=network.target

[Service]
User=icc
Group=www-data
WorkingDirectory=/srv/icc/app/backend
ExecStart=/srv/icc/app/backend/.venv/bin/gunicorn config.wsgi:application \
    --workers 3 --bind unix:/run/icc-backend/gunicorn.sock --timeout 60
RuntimeDirectory=icc-backend
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload && sudo systemctl enable --now icc-backend
```

Несколько воркеров с SQLite работают нормально: включены WAL и `transaction_mode=IMMEDIATE`, а кэш для лимита запросов — общий, в базе (`DatabaseCache`).

## 5. nginx

`/etc/nginx/sites-available/icc-backend`:

```nginx
server {
    listen 80;
    server_name api.<домен>;
    return 301 https://$host$request_uri;   # редирект на HTTPS — здесь (см. W008)
}

server {
    listen 443 ssl;
    server_name api.<домен>;
    # ssl_certificate ... — добавит certbot

    client_max_body_size 25m;   # документы до 20 МБ + запас

    location /static/ { alias /srv/icc/app/backend/staticfiles/; expires 30d; }
    location /media/  {
        alias /srv/icc/app/backend/media/;
        expires 7d;
        types { image/webp webp; }
        include /etc/nginx/mime.types;
    }

    location / {
        proxy_pass http://unix:/run/icc-backend/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/icc-backend /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d api.<домен>      # Let's Encrypt, продление — автоматически
```

## 6. `NUM_PROXIES` и IP клиента

Бэк берёт IP клиента для лимита формы (5 в час), блокировки входа (axes) и поля «IP» в обращении по правилу: при `NUM_PROXIES=N` — **N-й адрес с конца** заголовка `X-Forwarded-For`.

- Браузер → nginx → Django (админка, API напрямую): `NUM_PROXIES=1`.
- **Форма обращения идёт через сервер Next.js** (`frontend/app/api/feedback/route.ts`): браузер → nginx фронта → Next.js → (nginx бэка?) → Django. Next.js пересылает полученный `X-Forwarded-For`. Если запрос от Next.js проходит через nginx бэка, nginx дописывает в конец адрес Next.js, и реальный клиент оказывается вторым с конца. Тогда для формы нужен `NUM_PROXIES=2`, а для админки — 1.

**Решение до запуска (с фронтендом):** чтобы одна настройка подходила обоим путям, Next.js должен ходить в Django **напрямую** (внутренний адрес, мимо nginx бэка) и передавать `X-Forwarded-For` от своего nginx. Тогда `NUM_PROXIES=1` верно в обоих случаях. Проверка: отправить форму с сайта и посмотреть IP обращения в админке — там должен быть ваш внешний IP, а не адрес сервера.

## 7. Бэкапы (14 дней)

`/srv/icc/backup.sh` (владелец `icc`, права `700`):

```bash
#!/bin/sh
set -e
DIR=/srv/icc/backups
STAMP=$(date +%Y-%m-%d)
mkdir -p "$DIR"
# онлайн-копия SQLite (корректна при работающем сайте, в отличие от cp)
sqlite3 /srv/icc/app/backend/db.sqlite3 ".backup '$DIR/db-$STAMP.sqlite3'"
gzip -f "$DIR/db-$STAMP.sqlite3"
tar -czf "$DIR/media-$STAMP.tar.gz" -C /srv/icc/app/backend media
find "$DIR" -type f -mtime +14 -delete
```

cron пользователя `icc` (`crontab -e`): `30 3 * * * /srv/icc/backup.sh`

Хранить копии лучше и вне сервера (rsync / object storage) — решить с заказчиком.

**Восстановление:** остановить gunicorn, распаковать `db-<дата>.sqlite3.gz` в `db.sqlite3`, распаковать `media`, запустить gunicorn.

## 8. HSTS и HTTPS: что решить при выборе домена

`check --deploy` при `DEBUG=False` оставляет три предупреждения. Их оставили осознанно (SPEC.md, «После MVP»):

| Код | Настройка | Почему пока не включено |
|---|---|---|
| W005 | `SECURE_HSTS_INCLUDE_SUBDOMAINS` | Браузеры перестанут открывать **все** поддомены домена по http. Включать, только если все поддомены заказчика работают по HTTPS |
| W021 | `SECURE_HSTS_PRELOAD` | Попадание в preload-список браузеров почти необратимо. Решать после стабильной работы HTTPS |
| W008 | `SECURE_SSL_REDIRECT` | Редирект на HTTPS делает nginx (раздел 5). Если nginx не настроен на редирект, включить в settings |

## 9. Логи и обновление

- Логи приложения: `backend/logs/app.log` (ротация 5 МБ × 5) — ошибки 500, неудачные входы и блокировки, ошибки почты. Плюс `journalctl -u icc-backend`.
- Обновление:
  ```bash
  cd /srv/icc/app && sudo -u icc git pull
  cd backend && sudo -u icc .venv/bin/pip install -r requirements.txt
  sudo -u icc .venv/bin/python manage.py migrate
  sudo -u icc .venv/bin/python manage.py collectstatic --noinput
  sudo systemctl restart icc-backend
  ```

## 10. Переезд на PostgreSQL (если понадобится)

Код использует только переносимые возможности ORM. Порядок переезда: `dumpdata` → смена `DATABASES` в settings → `migrate` → `loaddata`. Файлы `media/` переносятся как есть.
