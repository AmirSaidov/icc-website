from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils import timezone

from apps.core.fields import NullableSlugField, unique_slug_constraints
from apps.core.models import PublishableModel, SeoModel, TimeStampedModel
from apps.core.sanitize import sanitize_translated_fields


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


class News(TimeStampedModel, PublishableModel, SeoModel):
    title = models.CharField("заголовок", max_length=255)
    slug = NullableSlugField("slug")
    excerpt = models.TextField("анонс", blank=True)
    content = models.TextField("содержимое", blank=True)
    cover = models.ImageField("обложка", upload_to="news/%Y/%m/", blank=True)
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

    title = models.CharField("заголовок", max_length=255)
    slug = NullableSlugField("slug")
    type = models.CharField("тип", max_length=20, choices=Type.choices)
    start_at = models.DateTimeField("начало", db_index=True)
    end_at = models.DateTimeField("окончание", null=True, blank=True)
    location = models.CharField("место проведения", max_length=255, blank=True)
    excerpt = models.TextField("анонс", blank=True)
    content = models.TextField("содержимое", blank=True)
    cover = models.ImageField("обложка", upload_to="events/%Y/%m/", blank=True)

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
        sanitize_translated_fields(self, "content")
        super().save(*args, **kwargs)
