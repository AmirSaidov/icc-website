"""
python manage.py seed [--flush]

Тестовые данные на трёх языках (SPEC.md, 5.4). Повторный запуск без --flush
не создаёт дублей: записи ищутся по стабильному ключу (slug_ru, код страны и т.п.)
и пропускаются, если уже есть. --flush удаляет seed-записи (вместе с файлами)
и создаёт их заново. Пользователей admin / editor seed только создаёт, если их нет:
существующие не удаляются и их пароли не меняются.
"""
import io
import secrets
from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import FileField, ProtectedError
from django.utils import timezone, translation
from PIL import Image, ImageDraw, ImageFont

from apps.cooperation.models import Country, Partner, Project
from apps.core import seed_data as data
from apps.core.i18n import LANGS
from apps.core.images import image_versions
from apps.core.models import Attachment, ContactInfo, GalleryImage, PublishableModel, SiteSettings
from apps.core.slugs import make_slug
from apps.news.models import Event, News, NewsCategory
from apps.pages.models import Direction, HomeBlock, Page, Service

PUBLISHED = PublishableModel.Status.PUBLISHED

PALETTE = [
    (31, 78, 121), (192, 57, 43), (39, 174, 96), (142, 68, 173),
    (211, 84, 0), (22, 160, 133), (44, 62, 80), (243, 156, 18),
]


# --- Заглушки файлов (Pillow, без интернета) ---------------------------------


def make_image(label, index, size=(1600, 900)):
    image = Image.new("RGB", size, PALETTE[index % len(PALETTE)])
    draw = ImageDraw.Draw(image)
    width, height = size
    draw.rectangle([width * 0.08, height * 0.3, width * 0.92, height * 0.7], fill=(255, 255, 255))
    font = ImageFont.load_default(size=max(24, height // 10))
    draw.text((width / 2, height / 2), label, fill=(40, 40, 40), font=font, anchor="mm")
    buffer = io.BytesIO()
    image.save(buffer, "JPEG", quality=85)
    return ContentFile(buffer.getvalue(), name=f"{label.lower().replace(' ', '-')}.jpg")


def make_pdf(label, name):
    image = Image.new("RGB", (1240, 1754), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.text((100, 100), label, fill=(0, 0, 0), font=ImageFont.load_default(size=48))
    buffer = io.BytesIO()
    image.save(buffer, "PDF")
    return ContentFile(buffer.getvalue(), name=name)


# --- Переводимые значения ----------------------------------------------------


def tr(field, values):
    """("ru", "en", "zh") → {"field_ru": ..., ...}; None — перевода нет (NULL)."""
    return {f"{field}_{lang}": value for lang, value in zip(LANGS, values) if value is not None}


def slugs(titles):
    return {f"slug_{lang}": make_slug(title, lang) for lang, title in zip(LANGS, titles) if title}


def at_10(days):
    """Дата относительно сегодня, 10:00 по Бишкеку."""
    base = timezone.localtime().replace(hour=10, minute=0, second=0, microsecond=0)
    return base + timedelta(days=days)


class Command(BaseCommand):
    help = "Заполняет базу тестовыми данными на трёх языках (ru / en / zh)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Удалить старые seed-данные (и их файлы) перед созданием.",
        )

    def handle(self, *args, flush=False, **options):
        self.flush_mode = flush
        self.created = {}
        self.skipped = {}
        self.image_index = 0
        with translation.override("ru"), transaction.atomic():
            if flush:
                self.flush()
            self.seed_system_pages()
            self.seed_singletons()
            self.seed_home_blocks()
            self.seed_directions()
            self.seed_services()
            categories = self.seed_news_categories()
            self.seed_news(categories)
            self.seed_events()
            countries = self.seed_countries()
            partners = self.seed_partners(countries)
            self.seed_projects(countries, partners)
            self.seed_documents()
            passwords = self.seed_users()
        self.warm_previews()
        self.report(passwords)

    # --- служебное ---

    def next_image(self, label):
        self.image_index += 1
        return make_image(label, self.image_index)

    def ensure(self, model, lookup, images=None, **fields):
        """
        Создаёт запись, если её ещё нет (поиск по lookup). Возвращает (obj, created).
        images: {"поле": "подпись"} — картинки-заглушки генерируются только для новых записей.
        """
        name = model._meta.verbose_name_plural
        obj = model.objects.filter(**lookup).first()
        if obj is not None:
            self.skipped[name] = self.skipped.get(name, 0) + 1
            return obj, False
        for field, label in (images or {}).items():
            fields[field] = self.next_image(label)
        obj = model(**{**fields, **lookup})
        obj.save()
        self.created[name] = self.created.get(name, 0) + 1
        return obj, True

    def add_gallery(self, obj, count):
        for order, caption in enumerate(data.GALLERY_CAPTIONS[:count]):
            GalleryImage.objects.create(
                content_object=obj,
                image=self.next_image(f"Photo {order + 1}"),
                order=order,
                **tr("caption", caption),
            )

    def add_program(self, obj):
        Attachment.objects.create(
            content_object=obj,
            file=make_pdf("Programme (seed)", "programme.pdf"),
            **tr("title", data.PROGRAM_TITLE),
        )

    # --- очистка ---

    @staticmethod
    def delete_files(obj):
        for field in obj._meta.concrete_fields:
            if isinstance(field, FileField):
                getattr(obj, field.name).delete(save=False)

    def delete_with_files(self, queryset):
        for obj in queryset:
            for relation in ("gallery", "attachments"):
                if hasattr(obj, relation):
                    for item in getattr(obj, relation).all():
                        self.delete_files(item)
            self.delete_files(obj)
            obj.delete()

    def flush(self):
        news_slugs = [make_slug(item[2][0], "ru") for item in data.NEWS]
        event_slugs = [make_slug(item[4][0], "ru") for item in data.EVENTS]
        project_slugs = [make_slug(item[3][0], "ru") for item in data.PROJECTS]
        self.delete_with_files(Project.objects.filter(slug_ru__in=project_slugs))
        self.delete_with_files(Partner.objects.filter(name_ru__in=[p[3][0] for p in data.PARTNERS]))
        for code, _, _ in data.COUNTRIES:
            try:
                self.delete_with_files(Country.objects.filter(code=code))
            except ProtectedError:
                self.stdout.write(self.style.WARNING(f"Страна {code} используется не-seed записями — оставлена."))
        self.delete_with_files(News.objects.filter(slug_ru__in=news_slugs))
        NewsCategory.objects.filter(slug_ru__in=[c[0] for c in data.NEWS_CATEGORIES]).delete()
        self.delete_with_files(Event.objects.filter(slug_ru__in=event_slugs))
        self.delete_with_files(Direction.objects.filter(slug_ru__in=[make_slug(d[1][0], "ru") for d in data.DIRECTIONS]))
        self.delete_with_files(Service.objects.filter(slug_ru__in=[make_slug(s[0][0], "ru") for s in data.SERVICES]))
        for block in data.HOME_BLOCKS:
            self.delete_with_files(HomeBlock.objects.filter(type=block["type"], title_ru=block["title"][0]))
        self.delete_with_files(
            Attachment.objects.filter(show_in_documents=True, title_ru=data.REGULATIONS_TITLE[0])
        )
        self.stdout.write("Старые seed-данные удалены.")

    # --- данные ---

    def seed_system_pages(self):
        for key, page_data in data.SYSTEM_PAGES.items():
            page = Page.objects.get(key=key)
            # Без --flush не перетираем то, что уже заполнил редактор.
            if page.title_en and not self.flush_mode:
                self.skipped["страницы"] = self.skipped.get("страницы", 0) + 1
                continue
            for field in ("title", "content", "meta_title", "meta_description"):
                if field in page_data:
                    for attr, value in tr(field, page_data[field]).items():
                        setattr(page, attr, value)
            page.show_in_menu = page_data["show_in_menu"]
            page.status = PUBLISHED
            page.save()
            self.created["страницы"] = self.created.get("страницы", 0) + 1

    def seed_singletons(self):
        contacts = ContactInfo.load()
        if self.flush_mode or not contacts.official_name_ru:
            for field in ("official_name", "address", "work_hours"):
                for attr, value in tr(field, data.CONTACTS[field]).items():
                    setattr(contacts, attr, value)
            for field in ("phones", "email", "map_lat", "map_lng", "socials"):
                setattr(contacts, field, data.CONTACTS[field])
            contacts.save()
        site = SiteSettings.load()
        if self.flush_mode or not site.default_og_image:
            if site.default_og_image:
                site.default_og_image.delete(save=False)
            site.default_og_image = make_image("ICC Kyrgyzstan", 0, size=(1200, 630))
            site.save()

    def seed_home_blocks(self):
        for order, block in enumerate(data.HOME_BLOCKS):
            fields = {
                **tr("title", block["title"]),
                **tr("text", block["text"]),
                **tr("button_text", block["button_text"]),
                "button_link": block["button_link"],
                "order": order,
                "status": PUBLISHED,
            }
            self.ensure(
                HomeBlock,
                {"type": block["type"], "title_ru": block["title"][0]},
                images={"image": block["type"].upper()} if block["image"] else None,
                **fields,
            )

    def seed_directions(self):
        for order, (icon, title, short_text) in enumerate(data.DIRECTIONS):
            self.ensure(
                Direction,
                {"slug_ru": make_slug(title[0], "ru")},
                **tr("title", title),
                **slugs(title),
                **tr("short_text", short_text),
                **tr("content", tuple(f"<p>{s}</p>" + data.LOREM[i] for i, s in enumerate(short_text))),
                icon=icon,
                order=order,
                status=PUBLISHED,
            )

    def seed_services(self):
        for order, (title, short_text) in enumerate(data.SERVICES):
            content = tuple(None if s is None else f"<p>{s}</p>" + data.LOREM[i] for i, s in enumerate(short_text))
            how_to_apply = (
                "Оставьте заявку через форму на сайте или позвоните нам.",
                "Send a request via the website form or call us.",
                None if title[2] is None else "通过网站表单提交申请或致电我们。",
            )
            contact_person = ("Иванова Анна", "Anna Ivanova", None if title[2] is None else "安娜·伊万诺娃")
            self.ensure(
                Service,
                {"slug_ru": make_slug(title[0], "ru")},
                **tr("title", title),
                **slugs(title),
                **tr("short_text", short_text),
                **tr("content", content),
                **tr("how_to_apply", how_to_apply),
                **tr("contact_person", contact_person),
                contact_email="services@example.kg",
                contact_phone="+996 312 000 002",
                order=order,
                status=PUBLISHED,
            )

    def seed_news_categories(self):
        categories = {}
        for order, (key, name) in enumerate(data.NEWS_CATEGORIES):
            # slug категорий — короткие латинские ключи, одинаковые по смыслу на всех языках
            category, _ = self.ensure(
                NewsCategory,
                {"slug_ru": key},
                **tr("name", name),
                slug_en=key,
                slug_zh=key,
                order=order,
            )
            categories[key] = category
        return categories

    def seed_news(self, categories):
        for index, (category, days_ago, title, excerpt) in enumerate(data.NEWS):
            content = tuple(None if e is None else f"<p>{e}</p>" + data.LOREM[i] for i, e in enumerate(excerpt))
            fields = {
                **tr("title", title),
                **slugs(title),
                **tr("excerpt", excerpt),
                **tr("content", content),
                "category": categories[category],
                "published_at": at_10(-days_ago),
                "status": PUBLISHED,
            }
            if index == 0:
                fields.update(tr("meta_title", (
                    "Деловая миссия в Урумчи — ЦПК", "Business mission to Urumqi — ICC", "乌鲁木齐商务考察 — 工业合作中心",
                )))
            news, created = self.ensure(
                News, {"slug_ru": make_slug(title[0], "ru")}, images={"cover": f"News {index + 1}"}, **fields
            )
            if created and index == 0:
                self.add_gallery(news, 3)
                self.add_program(news)

    def seed_events(self):
        for index, (event_type, start_days, duration, place, title, excerpt) in enumerate(data.EVENTS):
            start_at = at_10(start_days)
            fields = {
                **tr("title", title),
                **slugs(title),
                **tr("excerpt", excerpt),
                **tr("content", tuple(f"<p>{e}</p>" + data.LOREM[i] for i, e in enumerate(excerpt))),
                **tr("location", data.LOCATIONS[place]),
                "type": event_type,
                "start_at": start_at,
                "end_at": start_at + timedelta(days=duration) if duration else None,
                "status": PUBLISHED,
            }
            event, created = self.ensure(
                Event, {"slug_ru": make_slug(title[0], "ru")}, images={"cover": f"Event {index + 1}"}, **fields
            )
            if created and index == 0:
                self.add_gallery(event, 2)
            elif created and index == 5:
                self.add_program(event)

    def seed_countries(self):
        countries = {}
        for order, (code, name, description) in enumerate(data.COUNTRIES):
            fields = {
                **tr("name", name),
                **tr("description", description),
                "is_active": True,
                "order": order,
            }
            country, _ = self.ensure(Country, {"code": code}, images={"flag": code}, **fields)
            countries[code] = country
        return countries

    def seed_partners(self, countries):
        partners = []
        for order, (code, consent, website, name, description) in enumerate(data.PARTNERS):
            fields = {
                **tr("name", name),
                **tr("description", description),
                "country": countries[code],
                "consent_to_publish": consent,
                "website": website,
                "order": order,
            }
            partner, _ = self.ensure(
                Partner, {"name_ru": name[0]}, images={"logo": f"Logo {order + 1}"}, **fields
            )
            partners.append(partner)
        return partners

    def seed_projects(self, countries, partners):
        for index, (code, days_ago, partner_indexes, title, excerpt) in enumerate(data.PROJECTS):
            fields = {
                **tr("title", title),
                **slugs(title),
                **tr("excerpt", excerpt),
                **tr("content", tuple(f"<p>{e}</p>" + data.LOREM[i] for i, e in enumerate(excerpt))),
                "country": countries[code],
                "published_at": at_10(-days_ago),
                "status": PUBLISHED,
            }
            project, created = self.ensure(
                Project, {"slug_ru": make_slug(title[0], "ru")}, images={"cover": f"Project {index + 1}"}, **fields
            )
            if not created:
                continue
            project.partners.set([partners[i] for i in partner_indexes])
            if index == 0:
                self.add_gallery(project, 2)

    def seed_documents(self):
        self.ensure(
            Attachment,
            {"show_in_documents": True, "title_ru": data.REGULATIONS_TITLE[0]},
            **tr("title", data.REGULATIONS_TITLE),
            file=make_pdf("Regulations of the Centre (seed stub)", "polozhenie-o-centre.pdf"),
        )

    def seed_users(self):
        passwords = {}
        for username, group_name, is_superuser in data.SEED_USERS:
            group = Group.objects.get(name=group_name)
            existing = User.objects.filter(username=username).first()
            if existing is not None:
                # Существующих пользователей не удаляем и пароль не меняем (даже с --flush) —
                # это может быть настоящий аккаунт. Только добавляем в группу роли.
                existing.groups.add(group)
                passwords[username] = None
                continue
            password = secrets.token_urlsafe(12)
            if is_superuser:
                user = User.objects.create_superuser(username, "", password)
            else:
                user = User.objects.create_user(username, "", password, is_staff=True)
            user.groups.add(group)
            passwords[username] = password
        return passwords

    # --- превью и отчёт ---

    def warm_previews(self):
        """Заранее генерирует WebP-превью, чтобы первый запрос к API не ждал."""
        targets = [
            (HomeBlock, "image"), (News, "cover"), (Event, "cover"), (Project, "cover"),
            (Country, "flag"), (Partner, "logo"), (GalleryImage, "image"),
        ]
        for model, field in targets:
            for obj in model.objects.exclude(**{field: ""}):
                image_versions(getattr(obj, field))
        image_versions(SiteSettings.load().default_og_image)

    def report(self, passwords):
        self.stdout.write(self.style.SUCCESS("Seed завершён."))
        for name in sorted(set(self.created) | set(self.skipped)):
            self.stdout.write(
                f"  {name}: создано {self.created.get(name, 0)}, уже было {self.skipped.get(name, 0)}"
            )
        self.stdout.write("Пользователи:")
        for username, password in passwords.items():
            if password:
                self.stdout.write(self.style.WARNING(f"  {username} / {password}"))
            else:
                self.stdout.write(f"  {username} — уже существует, пароль не менялся")
