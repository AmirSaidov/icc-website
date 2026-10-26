from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MaxLengthValidator, RegexValidator
from django.db import models
from django.utils import timezone

from apps.core.api import is_published
from apps.core.fields import (
    ImageUploadField,
    NullableSlugField,
    PresentationPdfField,
    PresentationPptxField,
    unique_slug_constraints,
)
from apps.core.files import count_pdf_pages
from apps.core.models import PublishableModel, SeoModel, TimeStampedModel
from apps.core.sanitize import sanitize_translated_fields
from apps.core.slugs import fill_translated_slugs


class Country(TimeStampedModel):
    name = models.CharField("название", max_length=255)
    code = models.CharField(
        "код ISO 3166-1 alpha-2",
        max_length=2,
        unique=True,
        validators=[RegexValidator(r"^[A-Z]{2}$", "Две заглавные латинские буквы, например CN.")],
    )
    flag = ImageUploadField("флаг", upload_to="flags/", blank=True)
    description = models.TextField("описание", blank=True)
    is_active = models.BooleanField("активна", default=True)
    order = models.PositiveIntegerField("порядок", default=0)

    class Meta:
        verbose_name = "страна"
        verbose_name_plural = "страны"
        ordering = ["order", "id"]

    def __str__(self):
        return self.name_ru or self.code


class Partner(TimeStampedModel):
    name = models.CharField("название", max_length=255)
    logo = ImageUploadField("логотип", upload_to="partners/", blank=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="partners",
        verbose_name="страна",
    )
    website = models.URLField("сайт", blank=True)
    description = models.TextField("описание", blank=True)
    consent_to_publish = models.BooleanField("согласие на публикацию", default=False)
    order = models.PositiveIntegerField("порядок", default=0)

    class Meta:
        verbose_name = "партнёр"
        verbose_name_plural = "партнёры"
        ordering = ["order", "id"]

    def __str__(self):
        return self.name_ru or f"Партнёр #{self.pk}"


class Project(TimeStampedModel, PublishableModel, SeoModel):
    title = models.CharField("заголовок", max_length=255)
    slug = NullableSlugField("slug")
    excerpt = models.TextField("анонс", blank=True)
    content = models.TextField("содержимое", blank=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="projects",
        verbose_name="страна",
    )
    partners = models.ManyToManyField(
        Partner,
        blank=True,
        related_name="projects",
        verbose_name="партнёры",
    )
    cover = ImageUploadField("обложка", upload_to="projects/%Y/%m/", blank=True)
    published_at = models.DateTimeField("дата публикации", default=timezone.now, db_index=True)

    gallery = GenericRelation("core.GalleryImage", related_query_name="project")
    attachments = GenericRelation("core.Attachment", related_query_name="project")

    class Meta:
        verbose_name = "международный проект"
        verbose_name_plural = "международные проекты"
        ordering = ["-published_at", "-id"]
        constraints = unique_slug_constraints("cooperation_project")

    def __str__(self):
        return self.title_ru or f"Проект #{self.pk}"

    def save(self, *args, **kwargs):
        fill_translated_slugs(self)
        sanitize_translated_fields(self, "content")
        super().save(*args, **kwargs)


# Файлы презентаций (PDF и PPTX) лежат в media/presentations/: для этого пути при раздаче
# вместо X-Frame-Options: DENY отдаётся frame-ancestors с FRONTEND_URL (apps.core.media).
# Обложки — отдельно, это обычные картинки.
PRESENTATION_FILES_DIR = "presentations"


class Sector(TimeStampedModel):
    """Сфера презентаций: «Промышленность», «Информационные технологии», …"""

    name = models.CharField("название", max_length=255)
    slug = NullableSlugField("slug")
    order = models.PositiveIntegerField("порядок", default=0)

    class Meta:
        verbose_name = "сфера"
        verbose_name_plural = "сферы"
        ordering = ["order", "id"]
        constraints = unique_slug_constraints("cooperation_sector")

    def __str__(self):
        return self.name_ru or f"Сфера #{self.pk}"

    def save(self, *args, **kwargs):
        fill_translated_slugs(self, title_field="name")
        super().save(*args, **kwargs)


class Presentation(TimeStampedModel, PublishableModel, SeoModel):
    # Раздел в API (поле category): «Совместные проекты» — презентации опубликованных
    # проектов, остальные — «Промышленность и IT». Не хранится, вычисляется.
    CATEGORY_PROJECTS = "projects"
    CATEGORY_INDUSTRY = "industry"
    CATEGORIES = (CATEGORY_PROJECTS, CATEGORY_INDUSTRY)
    EXCERPT_MAX_LENGTH = 300

    title = models.CharField("заголовок", max_length=255)
    slug = NullableSlugField("slug")
    excerpt = models.TextField(
        "анонс",
        max_length=EXCERPT_MAX_LENGTH,
        blank=True,
        validators=[MaxLengthValidator(EXCERPT_MAX_LENGTH)],
        help_text="Короткий текст без оформления для карточки, до 300 символов.",
    )
    content = models.TextField("содержимое", blank=True)
    file = PresentationPdfField(
        "файл PDF",
        upload_to=f"{PRESENTATION_FILES_DIR}/%Y/%m/",
        max_length=255,
        help_text="Обязательно. По этому файлу презентация показывается на сайте. Только PDF, до 50 МБ.",
    )
    source_file = PresentationPptxField(
        "исходник PPTX",
        upload_to=f"{PRESENTATION_FILES_DIR}/%Y/%m/",
        max_length=255,
        blank=True,
        help_text="Необязательно. Только для скачивания. PPTX, до 50 МБ.",
    )
    cover = ImageUploadField("обложка", upload_to="presentation-covers/%Y/%m/", blank=True)
    sector = models.ForeignKey(
        Sector,
        on_delete=models.PROTECT,
        related_name="presentations",
        verbose_name="сфера",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="presentations",
        verbose_name="проект",
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="presentations",
        verbose_name="страна",
    )
    published_at = models.DateTimeField("дата публикации", default=timezone.now, db_index=True)
    order = models.PositiveIntegerField(
        "порядок", default=0, help_text="Порядок в списке презентаций на странице проекта."
    )
    # Заполняются автоматически при сохранении.
    size = models.PositiveBigIntegerField("размер PDF, байт", default=0, editable=False)
    pages = models.PositiveIntegerField("страниц", null=True, blank=True, editable=False)
    source_size = models.PositiveBigIntegerField("размер PPTX, байт", null=True, blank=True, editable=False)

    class Meta:
        verbose_name = "презентация"
        verbose_name_plural = "презентации"
        ordering = ["-published_at", "-id"]
        constraints = unique_slug_constraints("cooperation_presentation")

    def __str__(self):
        return self.title_ru or f"Презентация #{self.pk}"

    def save(self, *args, **kwargs):
        fill_translated_slugs(self)
        sanitize_translated_fields(self, "content")
        self.update_file_info()
        super().save(*args, **kwargs)

    @property
    def category(self):
        """projects — есть опубликованный проект (тот же фильтр, что ?category=), иначе industry."""
        if self.project_id and is_published(self.project):
            return self.CATEGORY_PROJECTS
        return self.CATEGORY_INDUSTRY

    def update_file_info(self):
        """size и pages — по новому PDF; source_size — по PPTX (нет файла — null)."""
        if self.file and (not self.file._committed or not self.size):
            self.size = self.file.size
            self.pages = count_pdf_pages(self.file)
        if not self.source_file:
            self.source_size = None
        elif not self.source_file._committed or self.source_size is None:
            self.source_size = self.source_file.size
