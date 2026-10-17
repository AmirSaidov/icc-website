from rest_framework import serializers

from apps.core.serializers import (
    HtmlField,
    ImageVersionsField,
    IsTranslatedField,
    NullableCharField,
    SeoField,
    SeoSerializer,
    TranslatedField,
)
from apps.news.serializers import EventListSerializer, NewsListSerializer

from .models import Direction, HomeBlock, Page, Service


class PageMenuSerializer(serializers.ModelSerializer):
    slug = TranslatedField(help_text="null у системных страниц — они адресуются по key")
    title = TranslatedField()

    class Meta:
        model = Page
        fields = ["key", "slug", "title", "order"]


class PageDetailSerializer(serializers.ModelSerializer):
    slug = TranslatedField(help_text="null у системных страниц — они адресуются по key")
    title = TranslatedField()
    content = HtmlField()
    is_translated = IsTranslatedField()
    seo = SeoField()

    class Meta:
        model = Page
        fields = ["id", "key", "slug", "title", "content", "is_translated", "seo"]


class HomeBlockSerializer(serializers.ModelSerializer):
    title = TranslatedField()
    text = TranslatedField()
    image = ImageVersionsField()
    button_text = TranslatedField()
    button_link = NullableCharField(
        help_text="Путь без языкового префикса, например /services. Префикс добавляет фронт."
    )
    is_translated = IsTranslatedField()

    class Meta:
        model = HomeBlock
        fields = [
            "id",
            "type",
            "title",
            "text",
            "image",
            "button_text",
            "button_link",
            "order",
            "is_translated",
        ]


class DirectionListSerializer(serializers.ModelSerializer):
    slug = TranslatedField()
    title = TranslatedField()
    short_text = TranslatedField()
    is_translated = IsTranslatedField()

    class Meta:
        model = Direction
        fields = ["id", "slug", "title", "short_text", "icon", "order", "is_translated"]


class DirectionDetailSerializer(DirectionListSerializer):
    content = HtmlField()
    seo = SeoField(description_field="short_text")

    class Meta(DirectionListSerializer.Meta):
        fields = ["id", "slug", "title", "short_text", "content", "icon", "order", "is_translated", "seo"]


class ServiceListSerializer(serializers.ModelSerializer):
    slug = TranslatedField()
    title = TranslatedField()
    short_text = TranslatedField()
    is_translated = IsTranslatedField()

    class Meta:
        model = Service
        fields = ["id", "slug", "title", "short_text", "order", "is_translated"]


class ServiceDetailSerializer(ServiceListSerializer):
    content = HtmlField()
    how_to_apply = TranslatedField()
    contact_person = TranslatedField()
    contact_email = NullableCharField()
    contact_phone = NullableCharField()
    seo = SeoField(description_field="short_text")

    class Meta(ServiceListSerializer.Meta):
        fields = [
            "id",
            "slug",
            "title",
            "short_text",
            "content",
            "how_to_apply",
            "contact_person",
            "contact_email",
            "contact_phone",
            "order",
            "is_translated",
            "seo",
        ]


class HomeSerializer(serializers.Serializer):
    """Всё для главной одним запросом. instance — dict, собранный во вьюхе."""

    blocks = HomeBlockSerializer(many=True, read_only=True)
    directions = DirectionListSerializer(many=True, read_only=True, help_text="Первые 4 по order")
    news = NewsListSerializer(many=True, read_only=True, help_text="3 последние")
    events = EventListSerializer(many=True, read_only=True, help_text="3 ближайших предстоящих")
    seo = SeoSerializer(read_only=True, help_text="Из страницы с key=home")
