from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.core.i18n import is_translated, translated_value
from apps.core.serializers import (
    AttachmentSerializer,
    GalleryImageSerializer,
    HtmlField,
    ImageVersionsField,
    IsTranslatedField,
    SeoField,
    TranslatedField,
)

from .models import Event, News, NewsCategory


class NewsCategorySerializer(serializers.ModelSerializer):
    slug = TranslatedField()
    name = TranslatedField()

    class Meta:
        model = NewsCategory
        fields = ["slug", "name"]


@extend_schema_field(NewsCategorySerializer(allow_null=True))
class CategoryField(serializers.Field):
    """Категория на языке запроса; null, если её нет или она не переведена на этот язык."""

    def __init__(self, **kwargs):
        kwargs["read_only"] = True
        super().__init__(**kwargs)

    def to_representation(self, category):
        lang = self.context["lang"]
        if not is_translated(category, lang):
            return None
        return {
            "slug": translated_value(category, "slug", lang),
            "name": translated_value(category, "name", lang),
        }


class NewsListSerializer(serializers.ModelSerializer):
    slug = TranslatedField()
    title = TranslatedField()
    excerpt = TranslatedField()
    cover = ImageVersionsField()
    category = CategoryField()
    is_translated = IsTranslatedField()

    class Meta:
        model = News
        fields = ["id", "slug", "title", "excerpt", "cover", "category", "published_at", "is_translated"]


class NewsDetailSerializer(NewsListSerializer):
    content = HtmlField()
    gallery = GalleryImageSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    seo = SeoField(description_field="excerpt", image_field="cover")

    class Meta(NewsListSerializer.Meta):
        fields = [
            "id",
            "slug",
            "title",
            "excerpt",
            "content",
            "cover",
            "category",
            "published_at",
            "gallery",
            "attachments",
            "is_translated",
            "seo",
        ]


class EventTypeSerializer(serializers.Serializer):
    code = serializers.ChoiceField(choices=Event.Type.choices)
    label = serializers.CharField(help_text="Подпись на языке запроса")


@extend_schema_field(EventTypeSerializer)
class EventTypeField(serializers.Field):
    def __init__(self, **kwargs):
        kwargs["read_only"] = True
        super().__init__(**kwargs)

    def to_representation(self, code):
        return {"code": code, "label": Event.type_label(code, self.context["lang"])}


class EventListSerializer(serializers.ModelSerializer):
    slug = TranslatedField()
    title = TranslatedField()
    type = EventTypeField()
    location = TranslatedField()
    excerpt = TranslatedField()
    cover = ImageVersionsField()
    is_upcoming = serializers.BooleanField(
        read_only=True, help_text="Вычисляется по end_at (если пусто — по start_at)"
    )
    is_translated = IsTranslatedField()

    class Meta:
        model = Event
        fields = [
            "id",
            "slug",
            "title",
            "type",
            "start_at",
            "end_at",
            "location",
            "excerpt",
            "cover",
            "is_upcoming",
            "is_translated",
        ]


class EventDetailSerializer(EventListSerializer):
    content = HtmlField()
    gallery = GalleryImageSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    seo = SeoField(description_field="excerpt", image_field="cover")

    class Meta(EventListSerializer.Meta):
        fields = [
            "id",
            "slug",
            "title",
            "type",
            "start_at",
            "end_at",
            "location",
            "excerpt",
            "content",
            "cover",
            "is_upcoming",
            "gallery",
            "attachments",
            "is_translated",
            "seo",
        ]
