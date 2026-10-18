# Деплой MVP: бэкенд на PythonAnywhere, фронтенд на Vercel

```
браузер ──> Vercel (Next.js, frontend/) ──API_URL──> PythonAnywhere (Django, backend/)
                 └─ /api/feedback (прокси формы) ──────────┘     └─ /media/ — картинки и файлы
```

Порядок важен: **сначала бэкенд, потом фронтенд**. `next build` на Vercel пререндерит страницы с данными из API: если бэк недоступен, сборка упадёт.

Ниже `<user>` — логин на PythonAnywhere, `<site>` — адрес проекта на Vercel (например, `icc-website.vercel.app`).

---

## 1. Бэкенд на PythonAnywhere

### 1.1. Код и окружение

В **Consoles → Bash**:

```bash
git clone https://github.com/AmirSaidov/icc-website.git
cd icc-website/backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 1.2. `.env`

Создать `~/icc-website/backend/.env` (в git не попадает):

```
SECRET_KEY=<python -c "import secrets; print(secrets.token_urlsafe(50))">
DEBUG=False
ALLOWED_HOSTS=<user>.pythonanywhere.com
CSRF_TRUSTED_ORIGINS=https://<user>.pythonanywhere.com
CORS_ALLOWED_ORIGINS=https://<site>
ADMIN_URL=<нестандартный путь, например cpk-7f3k9q/>
FRONTEND_URL=https://<site>
BACKEND_URL=https://<user>.pythonanywhere.com
NUM_PROXIES=2
EMAIL_HOST=
DEFAULT_FROM_EMAIL=noreply@example.kg
FEEDBACK_EMAIL=
```

- `NUM_PROXIES=2`: форма идёт по цепочке браузер → Vercel → прокси PythonAnywhere → Django, и реальный IP клиента стоит вторым с конца в `X-Forwarded-For`. При `1` бэк увидит IP Vercel, и лимит «5 обращений в час» станет общим на всех посетителей. Для прямых запросов (админка) в заголовке один адрес, и `2` тоже даёт правильный IP. Как проверить, см. раздел 3.
- `EMAIL_HOST` пустой: письма пишутся в лог (console backend). Бесплатный аккаунт PythonAnywhere не пускает на произвольные SMTP-серверы. Заявки в любом случае сохраняются и видны в админке.

### 1.3. База, статика, пользователи

```bash
python manage.py migrate
python manage.py createcachetable
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py check --deploy     # ожидаемы только W005, W008, W021 (backend/docs/DEPLOY.md, раздел 8)
```

Для демонстрации MVP можно залить тестовые данные: `python manage.py seed`. Это демо-контент, перед запуском для заказчика его нужно удалить (`seed --flush` пересоздаёт тестовые данные, а не удаляет их, поэтому чистить нужно в админке или пересозданием базы). `seed` также создаёт пользователей `admin` и `editor` с паролями в выводе консоли: на публичном сервере сразу сменить им пароли (`python manage.py changepassword admin`) или удалить их.

### 1.4. Веб-приложение

**Web → Add a new web app → Manual configuration → Python 3.12**, затем на странице приложения:

| Поле | Значение |
|---|---|
| Source code | `/home/<user>/icc-website/backend` |
| Virtualenv | `/home/<user>/icc-website/backend/.venv` |
| Static files: `/static/` | `/home/<user>/icc-website/backend/staticfiles` |
| Static files: `/media/` | `/home/<user>/icc-website/backend/media` |
| Force HTTPS | включить |

WSGI-файл (ссылка «WSGI configuration file») заменить целиком:

```python
import os
import sys

path = "/home/<user>/icc-website/backend"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Нажать **Reload**. Проверка:

- `https://<user>.pythonanywhere.com/api/v1/home/?lang=ru` → 200, ссылки на картинки начинаются с `https://<user>.pythonanywhere.com/media/`;
- `https://<user>.pythonanywhere.com/<ADMIN_URL>` → вход в админку, стили на месте.

### 1.5. Ограничения бесплатного аккаунта

- Веб-приложение отключается через 3 месяца, если не нажать **Run until 3 months from today** на вкладке Web.
- Исходящие соединения только к белому списку сайтов, поэтому почта через свой SMTP не работает (см. выше).
- Квота CPU в сутки. Для MVP хватает: Vercel кэширует страницы (ISR, 60 с) и ходит в API редко.

### 1.6. Обновление бэкенда

```bash
cd ~/icc-website && git pull
cd backend && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Затем **Reload** на вкладке Web.

---

## 2. Фронтенд на Vercel

1. **Add New → Project →** импортировать `AmirSaidov/icc-website`.
2. **Root Directory:** `frontend`. Framework определится сам (Next.js), команды сборки оставить по умолчанию.
3. **Environment Variables** (Production и Preview):

   | Переменная | Значение |
   |---|---|
   | `API_URL` | `https://<user>.pythonanywhere.com/api/v1` |
   | `NEXT_PUBLIC_SITE_URL` | `https://<site>` |

4. **Deploy.**

Если адрес проекта стал известен только после первого деплоя, нужно обновить `NEXT_PUBLIC_SITE_URL` и сделать **Redeploy**: переменные `NEXT_PUBLIC_*` вшиваются при сборке. Затем на PythonAnywhere обновить `FRONTEND_URL` и `CORS_ALLOWED_ORIGINS` в `.env` и нажать **Reload**: от `FRONTEND_URL` зависят ссылки в `sitemap.xml`.

Дальше каждый push в `main` деплоится автоматически. Правки в админке появляются на сайте в течение 60 секунд (ISR), передеплой для этого не нужен.

---

## 3. Проверка после деплоя

- [ ] `https://<site>/` → редирект на `/ru`; главная, «О Центре», направления, услуги, новости, мероприятия, сотрудничество и контакты открываются на ru / en / zh.
- [ ] Картинки грузятся (они идут с PythonAnywhere через `next/image`).
- [ ] Переключатель языка на новости ведёт на ту же новость на другом языке.
- [ ] `https://<site>/ru/news/no-such-news` → страница 404.
- [ ] Отправить форму на `/ru/contacts`: «Спасибо…», заявка появилась в админке.
- [ ] **IP в заявке** (админка → Обращения) совпадает с вашим внешним IP (например, по 2ip.ru), а не с адресом Vercel. Если там адрес Vercel или прокси, поменять `NUM_PROXIES` и перепроверить.

## 4. Известные ограничения MVP

- `NUM_PROXIES=2` доверяет второму с конца адресу в `X-Forwarded-For`. Кто шлёт POST прямо на PythonAnywhere, может подставить свой заголовок и обойти лимит формы. После MVP — секретный заголовок между Vercel и Django или свой сервер (backend/docs/DEPLOY.md).
- `sitemap.xml` и `robots.txt` отдаёт бэк со своего домена. Отдавать ли их с домена сайта — открытый вопрос (backend/SPEC.md, раздел 9).
- База — SQLite на диске PythonAnywhere. Бэкапы (backend/docs/DEPLOY.md, раздел 7) настроить вручную через **Tasks**.
