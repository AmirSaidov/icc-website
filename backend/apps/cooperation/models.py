from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from apps.core.fields import ImageUploadField, NullableSlugField, unique_slug_constraints
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
