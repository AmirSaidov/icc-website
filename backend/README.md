# Бэкенд сайта ЦПК при ТПП КР

API на трёх языках (ru / en / zh), админка с двумя ролями и приём обращений из форм для сайта Центра промышленной кооперации при Торгово-промышленной палате КР.

Стек: Python 3.12, Django 5.2, Django REST Framework, SQLite, django-modeltranslation.

Репозиторий общий с фронтендом (`frontend/`). **Все команды ниже выполняются из папки `backend/`.**

## Запуск на Windows за 5 команд

Нужны Python 3.12 (`py -3.12 --version`) и Git.

```
git clone https://github.com/AmirSaidov/icc-website.git
cd icc-website\backend
```

**Командная строка (cmd):**
```
py -3.12 -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate && python manage.py createcachetable
python manage.py seed && python manage.py runserver
```

**PowerShell** (в Windows PowerShell 5.1 вместо `&&` используется `;`):
```
py -3.12 -m venv .venv; .venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate; python manage.py createcachetable
python manage.py seed; python manage.py runserver
```
Если PowerShell пишет «выполнение сценариев отключено», выполните один раз `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` или используйте cmd.

`seed` заполняет базу тестовыми данными на трёх языках и создаёт пользователей `admin` (Администратор) и `editor` (Редактор). Пароли выводятся в консоль. Если такие пользователи уже есть, их пароли не меняются.

Для локального запуска `.env.example` подходит как есть. Для сервера см. [docs/DEPLOY.md](docs/DEPLOY.md).

## Что открыть после запуска

| Адрес | Что это |
|---|---|
| http://localhost:8000/api/docs/ | Swagger: все эндпоинты с примерами |
| http://localhost:8000/api/v1/ | Базовый адрес API |
| http://localhost:8000/admin/ | Админка (путь задаётся в `ADMIN_URL`) |
| http://localhost:8000/sitemap.xml | Sitemap (ссылки на фронт, `FRONTEND_URL`) |
| http://localhost:8000/robots.txt | robots.txt |

## Роли в админке

| Доступ | Администратор | Редактор |
|---|---|---|
| Страницы, блоки главной, направления, услуги, новости, мероприятия, страны, партнёры, проекты, сферы и презентации, фото, документы | полный | полный |
| Обращения из форм | полный, экспорт CSV | только статус и комментарий, экспорт CSV, без удаления |
| Контакты, настройки сайта | да | не видит |
| Пользователи и группы | да | не видит |
| Журналы входа (блокировки) | просмотр и снятие блокировки | не видит |

Группы создаются миграцией. Новому сотруднику нужно поставить «Статус персонала» и добавить его в одну из групп. Подробная инструкция для сотрудников — [docs/ADMIN_GUIDE.md](docs/ADMIN_GUIDE.md).

## Команды

| Команда | Что делает |
|---|---|
| `python manage.py seed` | Тестовые данные на трёх языках; повторный запуск не создаёт дублей |
| `python manage.py seed --flush` | Удалить тестовые данные (и их файлы) и создать заново |
| `python manage.py createsuperuser` | Создать суперпользователя |
| `python manage.py createcachetable` | Таблица кэша (нужна для лимита запросов формы) |
| `python manage.py export_api_examples` | Пересобрать примеры ответов для Swagger и `docs/API.md` (после `seed`) |
| `python manage.py spectacular --file docs/openapi.yaml --validate` | Пересобрать OpenAPI-схему |
| `python manage.py check --deploy` | Проверка настроек безопасности (с `DEBUG=False`) |

## Тесты

```
pytest
```
Тесты используют отдельную тестовую базу и временную папку для файлов, `db.sqlite3` и `media/` не затрагиваются. Соответствие тестов критериям из раздела 6 SPEC.md — в [docs/ACCEPTANCE.md](docs/ACCEPTANCE.md).

## Структура

```
backend/
  manage.py, requirements.txt, pytest.ini, conftest.py
  .env.example            # переменные окружения (.env не в git)
  config/                 # settings.py, urls.py, wsgi.py, asgi.py
  apps/
    core/                 # миксины, ContactInfo, SiteSettings, фото, документы;
                          # язык, slug, санитайзинг, валидация файлов, превью,
                          # seo, sitemap/robots, раздача media в dev, роли,
                          # команды seed и export_api_examples
    pages/                # Page, HomeBlock, Direction, Service; /home/, /pages/
    news/                 # NewsCategory, News, Event
    cooperation/          # Country, Partner, Project, Sector, Presentation
    feedback/             # Feedback, POST /feedback/, письма
  templates/              # страница блокировки входа
  static/                 # jQuery UI (локально), скрипты и стили админки
  docs/                   # API.md, openapi.yaml, ADMIN_GUIDE.md, DEPLOY.md, ACCEPTANCE.md
  media/  logs/  db.sqlite3   # создаются при работе, не в git
```

## Документация

- [SPEC.md](SPEC.md) — техническое задание бэкенда, единственный источник правды.
- [docs/API.md](docs/API.md) — API для фронтенда: язык, переводы, переключатель языка, пагинация, форма, примеры ответов.
- [docs/openapi.yaml](docs/openapi.yaml) — OpenAPI-схема (то же, что в Swagger).
- [docs/ADMIN_GUIDE.md](docs/ADMIN_GUIDE.md) — инструкция для сотрудников Центра.
- [docs/DEPLOY.md](docs/DEPLOY.md) — развёртывание на сервере (черновик на после MVP).
- [docs/ACCEPTANCE.md](docs/ACCEPTANCE.md) — приёмка: тесты раздела 6 и критерии раздела 8.
- [CLAUDE.md](CLAUDE.md) — правила проекта для разработки.
