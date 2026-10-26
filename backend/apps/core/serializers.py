"""
Общие поля и сериализаторы API.

Правило: переводимые поля читаются явно как <field>_<lang>; "" и NULL отдаются как null.
"""
import re
from pathlib import PurePosixPath

from django.conf import settings

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .i18n import is_translated, translated_value
from .images import absolute_url, image_versions
from .models import Attachment, ContactInfo, GalleryImage, SiteSettings
from .seo import build_seo

# --- Схемы для документации ---------------------------------------------------


class ImageVersionsSerializer(serializers.Serializer):
    small = serializers.URLField(help_text="WebP, ширина 400 px")
    large = serializers.URLField(help_text="WebP, ширина 1200 px")


class AlternatesSerializer(serializers.Serializer):
    ru = serializers.CharField(allow_null=True)
    en = serializers.CharField(allow_null=True)
    zh = serializers.CharField(allow_null=True)


class SeoSerializer(serializers.Serializer):
    meta_title = serializers.CharField(allow_null=True, help_text="Если пусто — title")
    meta_description = serializers.CharField(
        allow_null=True, help_text="Если пусто — excerpt / short_text"
    )
    og_image = serializers.URLField(
        allow_null=True, help_text="1200 px; если пусто — cover, затем default_og_image"
    )
    alternates = AlternatesSerializer(
        help_text="slug записи на каждом языке (null — не переведена). "
        "Для системных страниц — их key. Данные для переключателя языка и hreflang."
    )


class PhoneSerializer(serializers.Serializer):
    label = serializers.CharField(allow_null=True, help_text="Подпись на языке запроса")
    number = serializers.CharField()


class SocialSerializer(serializers.Serializer):
    type = serializers.CharField(help_text="Ключ иконки на фронте: telegram, facebook, ...")
    url = serializers.URLField()


# --- Поля ---------------------------------------------------------------------


class _ReadOnlyField(serializers.Field):
    def __init__(self, **kwargs):
        kwargs["read_only"] = True
        super().__init__(**kwargs)


@extend_schema_field({"type": "string", "nullable": True})
class TranslatedField(_ReadOnlyField):
    """Читает <source>_<lang> на языке из контекста; "" и NULL → null."""

    def get_attribute(self, instance):
        return translated_value(instance, self.source, self.context["lang"])

    def to_representation(self, value):
        return value or None


MEDIA_LINK_RE = re.compile(r'(\s(?:src|href)=")(%s[^"]*)"' % re.escape(settings.MEDIA_URL))


@extend_schema_field({"type": "string", "nullable": True, "description": "Безопасный HTML"})
class HtmlField(TranslatedField):
    """
    Rich text (content): безопасный HTML (очищен при сохранении). Ссылки на загруженные
    через редактор файлы (/media/...) превращаются в абсолютные URL.
    """

    def to_representation(self, value):
        if not value:
            return None
        request = self.context.get("request")
        if request is None:
            return value
        return MEDIA_LINK_RE.sub(
            lambda m: f'{m.group(1)}{request.build_absolute_uri(m.group(2))}"', value
        )


@extend_schema_field({"type": "string", "nullable": True})
class NullableCharField(_ReadOnlyField):
    """Непереводимая необязательная строка: "" → null."""

    def to_representation(self, value):
        return value or None


@extend_schema_field(ImageVersionsSerializer(allow_null=True))
class ImageVersionsField(_ReadOnlyField):
    """Картинка → {"small", "large"} с абсолютными URL или null."""

    def to_representation(self, value):
        return image_versions(value, self.context.get("request"))


@extend_schema_field(OpenApiTypes.BOOL)
class IsTranslatedField(_ReadOnlyField):
    def __init__(self, **kwargs):
        kwargs["source"] = "*"
        super().__init__(**kwargs)

    def to_representation(self, value):
        return is_translated(value, self.context["lang"])


@extend_schema_field(PhoneSerializer(many=True))
class PhonesField(_ReadOnlyField):
    """[{"label_ru", "label_en", "label_zh", "number"}] → [{"label", "number"}] на языке запроса."""

    def to_representation(self, value):
        lang = self.context["lang"]
        return [
            {"label": item.get(f"label_{lang}") or None, "number": item.get("number")}
            for item in value or []
        ]


def get_site_settings(context):
    """SiteSettings один раз на запрос (кеш в контексте сериализатора)."""
    if "_site_settings" not in context:
        context["_site_settings"] = SiteSettings.load()
    return context["_site_settings"]


@extend_schema_field(SeoSerializer)
class SeoField(_ReadOnlyField):
    def __init__(self, description_field=None, image_field=None, description_is_html=False, **kwargs):
        self.description_field = description_field
        self.image_field = image_field
        self.description_is_html = description_is_html
        kwargs["source"] = "*"
        super().__init__(**kwargs)

    def to_representation(self, value):
        return build_seo(
            value,
            self.context["lang"],
            self.context.get("request"),
            get_site_settings(self.context),
            description_field=self.description_field,
            image_field=self.image_field,
            description_is_html=self.description_is_html,
        )


# --- Сериализаторы ------------------------------------------------------------


class GalleryImageSerializer(serializers.ModelSerializer):
    small = serializers.URLField(read_only=True, help_text="WebP, ширина 400 px")
    large = serializers.URLField(read_only=True, help_text="WebP, ширина 1200 px")
    caption = TranslatedField()

    class Meta:
        model = GalleryImage
        fields = ["small", "large", "caption"]

    def to_representation(self, instance):
        versions = image_versions(instance.image, self.context.get("request")) or {}
        return {
            "small": versions.get("small"),
            "large": versions.get("large"),
            "caption": translated_value(instance, "caption", self.context["lang"]),
        }


class AttachmentSerializer(serializers.ModelSerializer):
    title = TranslatedField()
    url = serializers.SerializerMethodField(help_text="Абсолютный URL файла")
    ext = serializers.SerializerMethodField(help_text="Расширение файла: pdf, docx")

    class Meta:
        model = Attachment
        fields = ["title", "url", "size", "ext"]

    def get_url(self, obj) -> str:
        return absolute_url(obj.file.url, self.context.get("request"))

    def get_ext(self, obj) -> str:
        return PurePosixPath(obj.file.name).suffix.lstrip(".").lower()


class ContactInfoSerializer(serializers.ModelSerializer):
    official_name = TranslatedField()
    address = TranslatedField()
    work_hours = TranslatedField()
    email = NullableCharField()
    map_lat = serializers.FloatField(allow_null=True, read_only=True)
    map_lng = serializers.FloatField(allow_null=True, read_only=True)
    phones = PhonesField()
    socials = SocialSerializer(many=True, read_only=True)

    class Meta:
        model = ContactInfo
        fields = [
            "official_name",
            "address",
            "phones",
            "email",
            "work_hours",
            "map_lat",
            "map_lng",
            "socials",
        ]


class SiteSettingsPublicSerializer(serializers.ModelSerializer):
    analytics_id = NullableCharField()
    default_og_image = ImageVersionsField()

    class Meta:
        model = SiteSettings
        fields = ["analytics_id", "default_og_image"]
