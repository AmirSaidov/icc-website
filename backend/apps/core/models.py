from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import models

from .fields import DocumentUploadField, ImageUploadField

# --- Миксины (SPEC.md, 2.2) ---------------------------------------------------


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("создано", auto_now_add=True)
    updated_at = models.DateTimeField("изменено", auto_now=True)

    class Meta:
        abstract = True


class PublishableModel(models.Model):
    """Единственный флаг публикации — status. В публичном API видны только published."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        REVIEW = "review", "На проверке"
        PUBLISHED = "published", "Опубликовано"

    status = models.CharField(
        "статус",
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )

    class Meta:
        abstract = True


class SeoModel(models.Model):
    """meta_title и meta_description переводимые, og_image общая для всех языков."""

    meta_title = models.CharField("meta title", max_length=255, blank=True)
    meta_description = models.TextField("meta description", blank=True)
    og_image = ImageUploadField("OG-картинка", upload_to="seo/%Y/%m/", blank=True)

    class Meta:
        abstract = True


SEO_TRANSLATED_FIELDS = ("meta_title", "meta_description")


class SingletonModel(models.Model):
    """Ровно одна запись (pk=1). Создаётся миграцией, удалить нельзя."""

    singleton_pk = 1

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = self.singleton_pk
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionDenied(f"Запись «{self._meta.verbose_name}» удалить нельзя.")

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=cls.singleton_pk)
        return obj


# --- Привязка галереи и вложений ---------------------------------------------

# GalleryImage и Attachment привязываются к News, Event, Project.
ATTACHABLE_MODELS = models.Q(app_label="news", model__in=["news", "event"]) | models.Q(
    app_label="cooperation", model="project"
)


# --- Модели -------------------------------------------------------------------


class ContactInfo(SingletonModel, TimeStampedModel):
    official_name = models.CharField("официальное название", max_length=255, blank=True)
    address = models.CharField("адрес", max_length=500, blank=True)
    phones = models.JSONField(
        "телефоны",
        default=list,
        blank=True,
        help_text="Подписи на трёх языках и номер.",
    )
    email = models.EmailField("email", blank=True)
    work_hours = models.CharField("часы работы", max_length=255, blank=True)
    map_lat = models.DecimalField("широта", max_digits=9, decimal_places=6, null=True, blank=True)
    map_lng = models.DecimalField("долгота", max_digits=9, decimal_places=6, null=True, blank=True)
    socials = models.JSONField(
        "соцсети",
        default=list,
        blank=True,
        help_text="Тип — ключ иконки на фронте (telegram, facebook, instagram, ...) и ссылка.",
    )

    class Meta:
        verbose_name = "контактная информация"
        verbose_name_plural = "контактная информация"

    def __str__(self):
        return "Контактная информация"


class SiteSettings(SingletonModel, TimeStampedModel):
    feedback_emails = models.CharField(
        "email для заявок",
        max_length=500,
        blank=True,
        help_text="Адреса через запятую. Если пусто — используется FEEDBACK_EMAIL из .env.",
    )
    analytics_id = models.CharField("ID счётчика аналитики", max_length=100, blank=True)
    default_og_image = ImageUploadField("OG-картинка по умолчанию", upload_to="seo/", blank=True)

    class Meta:
        verbose_name = "настройки сайта"
        verbose_name_plural = "настройки сайта"

    def __str__(self):
        return "Настройки сайта"


class GalleryImage(TimeStampedModel):
    image = ImageUploadField("изображение", upload_to="gallery/%Y/%m/")
    caption = models.CharField("подпись", max_length=255, blank=True)
    order = models.PositiveIntegerField("порядок", default=0)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=ATTACHABLE_MODELS,
        verbose_name="тип объекта",
    )
    object_id = models.PositiveBigIntegerField("ID объекта")
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        verbose_name = "фото"
        verbose_name_plural = "фото"
        ordering = ["order", "id"]
        indexes = [models.Index(fields=["content_type", "object_id"])]

    def __str__(self):
        return self.caption or f"Фото #{self.pk}"


class Attachment(TimeStampedModel):
    file = DocumentUploadField("файл", upload_to="documents/%Y/%m/")
    title = models.CharField("название", max_length=255)
    size = models.PositiveBigIntegerField("размер, байт", default=0, editable=False)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        limit_choices_to=ATTACHABLE_MODELS,
        verbose_name="тип объекта",
    )
    object_id = models.PositiveBigIntegerField("ID объекта", null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")
    show_in_documents = models.BooleanField("показывать в «Документах»", default=False)
    order = models.PositiveIntegerField("порядок", default=0)

    class Meta:
        verbose_name = "документ"
        verbose_name_plural = "документы"
        ordering = ["order", "id"]
        indexes = [models.Index(fields=["content_type", "object_id"])]

    def __str__(self):
        return self.title or f"Документ #{self.pk}"

    def save(self, *args, **kwargs):
        if self.file:
            self.size = self.file.size
        super().save(*args, **kwargs)
