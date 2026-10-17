"""
python manage.py export_api_examples

Снимает реальные ответы API на текущей базе (после `seed`) и сохраняет их:
  - apps/core/api_examples/<name>.json — примеры ответов в Swagger (drf-spectacular);
  - docs/API.md — блок между маркерами <!-- examples:start --> / <!-- examples:end -->.

После неё обновите схему: python manage.py spectacular --file docs/openapi.yaml --validate
"""
import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from django.test import Client

from apps.cooperation.models import Project
from apps.core.api import published
from apps.core.schema import EXAMPLES_DIR
from apps.news.models import Event, News
from apps.pages.models import Direction, Service

API_MD = Path(settings.BASE_DIR) / "docs" / "API.md"
START, END = "<!-- examples:start -->", "<!-- examples:end -->"
LIST_LIMIT = 2  # в примерах списки сокращены до 2 элементов


def trim(value):
    if isinstance(value, list):
        return [trim(item) for item in value[:LIST_LIMIT]]
    if isinstance(value, dict):
        return {key: trim(item) for key, item in value.items()}
    return value


class Command(BaseCommand):
    help = "Сохраняет реальные ответы API (на seed-данных) как примеры для Swagger и docs/API.md."

    def add_arguments(self, parser):
        parser.add_argument("--host", default="localhost:8000", help="Хост в абсолютных URL примеров")

    def handle(self, *args, host, **options):
        news = published(News.objects.annotate(photos=Count("gallery"))).order_by("-photos", "-published_at").first()
        untranslated = published(News.objects.filter(title_zh__isnull=True)).first()
        event = published(Event.objects.annotate(photos=Count("gallery"))).order_by("-photos").first()
        project = published(Project.objects.annotate(photos=Count("gallery"))).order_by("-photos").first()
        direction = published(Direction.objects.order_by("order")).first()
        service = published(Service.objects.order_by("order")).first()
        if not all([news, untranslated, event, project, direction, service]):
            raise CommandError("Нет seed-данных. Сначала выполните: python manage.py seed")

        # (имя файла, заголовок в API.md, путь, параметры)
        examples = [
            ("home", "Главная", "/api/v1/home/", {"lang": "ru"}),
            ("pages_list", "Страницы для меню", "/api/v1/pages/", {"lang": "ru"}),
            ("page_detail", "Страница (системная, по key)", "/api/v1/pages/about/", {"lang": "en"}),
            ("directions_list", "Направления", "/api/v1/directions/", {"lang": "ru"}),
            ("direction_detail", "Направление", f"/api/v1/directions/{direction.slug_ru}/", {"lang": "ru"}),
            ("services_list", "Услуги", "/api/v1/services/", {"lang": "ru"}),
            ("service_detail", "Услуга", f"/api/v1/services/{service.slug_ru}/", {"lang": "ru"}),
            ("news_categories", "Категории новостей", "/api/v1/news-categories/", {"lang": "ru"}),
            ("news_list", "Новости", "/api/v1/news/", {"lang": "ru", "page_size": 2}),
            ("news_detail", "Новость", f"/api/v1/news/{news.slug_ru}/", {"lang": "ru"}),
            (
                "news_detail_untranslated",
                "Новость без перевода на zh (is_translated: false)",
                f"/api/v1/news/{untranslated.slug_ru}/",
                {"lang": "zh"},
            ),
            ("events_list", "Мероприятия (предстоящие)", "/api/v1/events/", {"lang": "ru", "when": "upcoming", "page_size": 2}),
            ("event_types", "Типы мероприятий", "/api/v1/event-types/", {"lang": "zh"}),
            ("event_detail", "Мероприятие", f"/api/v1/events/{event.slug_en}/", {"lang": "en"}),
            ("countries", "Страны", "/api/v1/countries/", {"lang": "ru"}),
            ("partners", "Партнёры", "/api/v1/partners/", {"lang": "ru", "country": "CN"}),
            ("projects_list", "Проекты", "/api/v1/projects/", {"lang": "ru", "page_size": 2}),
            ("project_detail", "Проект", f"/api/v1/projects/{project.slug_ru}/", {"lang": "zh"}),
            ("contacts", "Контакты", "/api/v1/contacts/", {"lang": "ru"}),
            ("settings", "Публичные настройки", "/api/v1/settings/", {"lang": "ru"}),
            ("documents", "Документы", "/api/v1/documents/", {"lang": "ru"}),
            ("error_lang", "Ошибка: невалидный lang (400)", "/api/v1/news/", {"lang": "de"}),
        ]

        client = Client(HTTP_HOST=host)
        EXAMPLES_DIR.mkdir(exist_ok=True)
        sections = []
        for name, title, path, params in examples:
            response = client.get(path, params)
            expected = 400 if name.startswith("error_") else 200
            if response.status_code != expected:
                raise CommandError(f"{path} {params} → {response.status_code}, ожидался {expected}")
            data = trim(response.json())
            text = json.dumps(data, ensure_ascii=False, indent=2)
            (EXAMPLES_DIR / f"{name}.json").write_text(text + "\n", encoding="utf-8")
            query = "&".join(f"{key}={value}" for key, value in params.items())
            sections.append(f"### {title}\n\n`GET {path}?{query}` → {response.status_code}\n\n```json\n{text}\n```\n")
            self.stdout.write(f"  {name}: {path}?{query}")

        if API_MD.exists():
            content = API_MD.read_text(encoding="utf-8")
            if START in content and END in content:
                head, rest = content.split(START, 1)
                _, tail = rest.split(END, 1)
                body = "\n".join(sections)
                API_MD.write_text(f"{head}{START}\n\n{body}\n{END}{tail}", encoding="utf-8")
                self.stdout.write(f"Обновлён {API_MD.relative_to(settings.BASE_DIR)}")
        self.stdout.write(self.style.SUCCESS(f"Примеры сохранены в {EXAMPLES_DIR.relative_to(settings.BASE_DIR)}"))
        self.stdout.write("Обновите схему: python manage.py spectacular --file docs/openapi.yaml --validate")
