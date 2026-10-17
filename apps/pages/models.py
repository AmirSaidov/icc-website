from django.core.exceptions import PermissionDenied
from django.db import models

from apps.core.fields import ImageUploadField, NullableSlugField, unique_slug_constraints
from apps.core.models import PublishableModel, SeoModel, TimeStampedModel
from apps.core.sanitize import sanitize_translated_fields
from apps.core.slugs import fill_translated_slugs


class Page(TimeStampedModel, PublishableModel, SeoModel):
    """Страница сайта. Системные страницы (с непустым key) создаются миграцией."""

    SYSTEM_KEYS = ("home", "about", "cooperation")
    # Системные страницы адресуются по key, slug им не нужен (SPEC.md, 2.1).
    system_key_field = "key"

    key = models.CharField(
        "системный ключ",
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="Только для системных страниц: home, about, cooperation.",
    )
    title = models.CharField("заголовок", max_length=255)
    slug = NullableSlugField("slug")
    content = models.TextField("содержимое", blank=True)
    show_in_menu = models.BooleanField("показывать в меню", default=False)
    order = models.PositiveIntegerField("порядок", default=0)

    class Meta:
        verbose_name = "страница"
        verbose_name_plural = "страницы"
        ordering = ["order", "id"]
        constraints = unique_slug_constraints("pages_page")

    def __str__(self):
        return self.title_ru or self.key or f"Страница #{self.pk}"

    @property
    def is_system(self):
        return bool(self.key)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = None
        fill_translated_slugs(self)
        sanitize_translated_fields(self, "content")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_system:
            raise PermissionDenied("Системную страницу удалить нельзя.")
        return super().delete(*args, **kwargs)


class HomeBlock(TimeStampedModel, PublishableModel):
    class Type(models.TextChoices):
        HERO = "hero", "Hero (первый экран)"
        ABOUT = "about", "О Центре"
        ADVANTAGES = "advantages", "Преимущества"
        KG_CHINA = "kg_china", "Кыргызстан — Китай"
        CTA = "cta", "Призыв к действию (CTA)"

    type = models.CharField("тип блока", max_length=20, choices=Type.choices)
    title = models.CharField("заголовок", max_length=255)
    text = models.TextField("текст", blank=True)
    image = ImageUploadField("изображение", upload_to="home/", blank=True)
    button_text = models.CharField("текст кнопки", max_length=100, blank=True)
    button_link = models.CharField(
        "ссылка кнопки",
        max_length=255,
        blank=True,
        help_text="Путь без языкового префикса, например /services. Префикс добавляет фронт.",
    )
    order = models.PositiveIntegerField("порядок", default=0)

    class Meta:
        verbose_name = "блок главной"
        verbose_name_plural = "блоки главной"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.get_type_display()}: {self.title_ru}"


class Direction(TimeStampedModel, PublishableModel, SeoModel):
    class Icon(models.TextChoices):
        # Смысловые ключи (SPEC.md, 2.3): фронт сам сопоставляет их с иконками.
        COOPERATION = "cooperation", "Кооперация"
        PARTNERSHIP = "partnership", "Партнёрство"
        JOINT_PRODUCTION = "joint-production", "Совместное производство"
        LOCALIZATION = "localization", "Локализация"
        SUBCONTRACTING = "subcontracting", "Субконтрактация"
        CONSULTING = "consulting", "Консалтинг"
        B2B_MEETINGS = "b2b-meetings", "B2B-встречи"
        EXPORT = "export", "Экспорт"

    title = models.CharField("заголовок", max_length=255)
    slug = NullableSlugField("slug")
    short_text = models.TextField("краткое описание", blank=True)
    content = models.TextField("содержимое", blank=True)
    icon = models.CharField(
        "иконка",
        max_length=50,
        choices=Icon.choices,
        help_text="Ключ иконки из набора фронта.",
    )
    order = models.PositiveIntegerField("порядок", default=0)

    class Meta:
        verbose_name = "направление"
        verbose_name_plural = "направления"
        ordering = ["order", "id"]
        constraints = unique_slug_constraints("pages_direction")

    def __str__(self):
        return self.title_ru or f"Направление #{self.pk}"

    def save(self, *args, **kwargs):
        fill_translated_slugs(self)
        sanitize_translated_fields(self, "content")
        super().save(*args, **kwargs)


class Service(TimeStampedModel, PublishableModel, SeoModel):
    title = models.CharField("заголовок", max_length=255)
    slug = NullableSlugField("slug")
    short_text = models.TextField("краткое описание", blank=True)
    content = models.TextField("содержимое", blank=True)
    how_to_apply = models.TextField("как обратиться", blank=True)
    contact_person = models.CharField("контактное лицо", max_length=255, blank=True)
    contact_email = models.EmailField("контактный email", blank=True)
    contact_phone = models.CharField("контактный телефон", max_length=30, blank=True)
    order = models.PositiveIntegerField("порядок", default=0)

    class Meta:
        verbose_name = "услуга"
        verbose_name_plural = "услуги"
        ordering = ["order", "id"]
        constraints = unique_slug_constraints("pages_service")

    def __str__(self):
        return self.title_ru or f"Услуга #{self.pk}"

    def save(self, *args, **kwargs):
        fill_translated_slugs(self)
        sanitize_translated_fields(self, "content")
        super().save(*args, **kwargs)
