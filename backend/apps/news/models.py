from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.core.fields import ImageUploadField, NullableSlugField, unique_slug_constraints
from apps.core.models import PublishableModel, SeoModel, TimeStampedModel
from apps.core.sanitize import sanitize_translated_fields
from apps.core.slugs import fill_translated_slugs


class NewsCategory(TimeStampedModel):
    name = models.CharField("название", max_length=255)
    slug = NullableSlugField("slug")
    order = models.PositiveIntegerField("порядок", default=0)

    class Meta:
        verbose_name = "категория новостей"
        verbose_name_plural = "категории новостей"
        ordering = ["order", "id"]
        constraints = unique_slug_constraints("news_newscategory")

    def __str__(self):
        return self.name_ru or f"Категория #{self.pk}"

    def save(self, *args, **kwargs):
        fill_translated_slugs(self, title_field="name")
        super().save(*args, **kwargs)


class News(TimeStampedModel, PublishableModel, SeoModel):
    title = models.CharField("заголовок", max_length=255)
    slug = NullableSlugField("slug")
    excerpt = models.TextField("анонс", blank=True)
    content = models.TextField("содержимое", blank=True)
    cover = ImageUploadField("обложка", upload_to="news/%Y/%m/", blank=True)
    category = models.ForeignKey(
        NewsCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="news",
        verbose_name="категория",
    )
    published_at = models.DateTimeField("дата публикации", default=timezone.now, db_index=True)

    gallery = GenericRelation("core.GalleryImage", related_query_name="news")
    attachments = GenericRelation("core.Attachment", related_query_name="news")

    class Meta:
        verbose_name = "новость"
        verbose_name_plural = "новости"
        ordering = ["-published_at", "-id"]
        constraints = unique_slug_constraints("news_news")

    def __str__(self):
        return self.title_ru or f"Новость #{self.pk}"

    def save(self, *args, **kwargs):
        fill_translated_slugs(self)
        sanitize_translated_fields(self, "content")
        super().save(*args, **kwargs)


class Event(TimeStampedModel, PublishableModel, SeoModel):
    """Мероприятие. «Предстоящее / прошедшее» не хранится — вычисляется по end_at / start_at."""

    class Type(models.TextChoices):
        MISSION = "mission", "Деловая миссия"
        FORUM = "forum", "Форум"
        EXHIBITION = "exhibition", "Выставка"
        B2B = "b2b", "B2B-встреча"
        OTHER = "other", "Другое"

    # Подписи типов для API (/event-types/, поле type.label) на языке запроса.
    TYPE_LABELS = {
        "mission": {"ru": "Деловая миссия", "en": "Business mission", "zh": "商务考察团"},
        "forum": {"ru": "Форум", "en": "Forum", "zh": "论坛"},
        "exhibition": {"ru": "Выставка", "en": "Exhibition", "zh": "展览会"},
        "b2b": {"ru": "B2B-встреча", "en": "B2B meeting", "zh": "B2B洽谈会"},
        "other": {"ru": "Другое", "en": "Other", "zh": "其他"},
    }

    title = models.CharField("заголовок", max_length=255)
    slug = NullableSlugField("slug")
    type = models.CharField("тип", max_length=20, choices=Type.choices)
    start_at = models.DateTimeField("начало", db_index=True)
    end_at = models.DateTimeField("окончание", null=True, blank=True)
    location = models.CharField("место проведения", max_length=255, blank=True)
    excerpt = models.TextField("анонс", blank=True)
    content = models.TextField("содержимое", blank=True)
    cover = ImageUploadField("обложка", upload_to="events/%Y/%m/", blank=True)

    gallery = GenericRelation("core.GalleryImage", related_query_name="event")
    attachments = GenericRelation("core.Attachment", related_query_name="event")

    class Meta:
        verbose_name = "мероприятие"
        verbose_name_plural = "мероприятия"
        ordering = ["-start_at", "-id"]
        constraints = unique_slug_constraints("news_event")

    def __str__(self):
        return self.title_ru or f"Мероприятие #{self.pk}"

    def save(self, *args, **kwargs):
        fill_translated_slugs(self)
        sanitize_translated_fields(self, "content")
        super().save(*args, **kwargs)

    # «Предстоящее / прошедшее» не хранится: по end_at, а если пусто — по start_at.
    @staticmethod
    def upcoming_q(now=None):
        now = now or timezone.now()
        return Q(end_at__gte=now) | Q(end_at__isnull=True, start_at__gte=now)

    @property
    def is_upcoming(self):
        return (self.end_at or self.start_at) >= timezone.now()

    @classmethod
    def type_label(cls, code, lang):
        return cls.TYPE_LABELS.get(code, {}).get(lang)
