from pathlib import PurePosixPath

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.core.api import is_published
from apps.core.i18n import is_translated, translated_value
from apps.core.images import absolute_url
from apps.core.serializers import (
    AttachmentSerializer,
    GalleryImageSerializer,
    HtmlField,
    ImageVersionsField,
    IsTranslatedField,
    NullableCharField,
    SeoField,
    TranslatedField,
)

from .models import Country, Partner, Presentation, Project, Sector


class CountryShortSerializer(serializers.ModelSerializer):
    name = TranslatedField()

    class Meta:
        model = Country
        fields = ["code", "name"]


class CountrySerializer(serializers.ModelSerializer):
    name = TranslatedField()
    description = TranslatedField()
    flag = ImageVersionsField()
    is_translated = IsTranslatedField()

    class Meta:
        model = Country
        fields = ["id", "code", "name", "description", "flag", "is_translated"]


class PartnerSerializer(serializers.ModelSerializer):
    name = TranslatedField()
    description = TranslatedField()
    logo = ImageVersionsField()
    country = CountryShortSerializer(read_only=True)
    website = NullableCharField()
    is_translated = IsTranslatedField()

    class Meta:
        model = Partner
        fields = ["id", "name", "logo", "country", "website", "description", "is_translated"]


# --- Презентации --------------------------------------------------------------


class SectorSerializer(serializers.ModelSerializer):
    slug = TranslatedField()
    name = TranslatedField()

    class Meta:
        model = Sector
        fields = ["slug", "name"]


class _RefField(serializers.Field):
    def __init__(self, **kwargs):
        kwargs["read_only"] = True
        super().__init__(**kwargs)


@extend_schema_field(SectorSerializer(allow_null=True))
class SectorField(_RefField):
    """Сфера на языке запроса; null, если она не переведена на этот язык."""

    def to_representation(self, sector):
        lang = self.context["lang"]
        if not is_translated(sector, lang):
            return None
        return {"slug": translated_value(sector, "slug", lang), "name": translated_value(sector, "name", lang)}


class ProjectRefSerializer(serializers.Serializer):
    slug = serializers.CharField()
    title = serializers.CharField()


@extend_schema_field(ProjectRefSerializer(allow_null=True))
class ProjectRefField(_RefField):
    """Проект презентации; null, если его нет, он не опубликован или не переведён на язык запроса."""

    def to_representation(self, project):
        lang = self.context["lang"]
        if not is_published(project) or not is_translated(project, lang):
            return None
        return {"slug": translated_value(project, "slug", lang), "title": translated_value(project, "title", lang)}


class PresentationFileSerializer(serializers.Serializer):
    url = serializers.URLField(help_text="Абсолютный URL PDF — для iframe или pdf.js")
    size = serializers.IntegerField(help_text="Размер, байт")
    pages = serializers.IntegerField(allow_null=True, help_text="Число страниц; null — не удалось посчитать")
    ext = serializers.CharField(help_text="Всегда pdf")


class PresentationSourceSerializer(serializers.Serializer):
    url = serializers.URLField(help_text="Абсолютный URL PPTX — только для скачивания")
    size = serializers.IntegerField(help_text="Размер, байт")
    ext = serializers.CharField(help_text="Всегда pptx")


def _ext(field_file):
    return PurePosixPath(field_file.name).suffix.lstrip(".").lower()


@extend_schema_field(PresentationFileSerializer)
class PresentationFileField(_RefField):
    def __init__(self, **kwargs):
        kwargs["source"] = "*"
        super().__init__(**kwargs)

    def to_representation(self, obj):
        return {
            "url": absolute_url(obj.file.url, self.context.get("request")),
            "size": obj.size,
            "pages": obj.pages,
            "ext": _ext(obj.file),
        }


@extend_schema_field(PresentationSourceSerializer(allow_null=True))
class PresentationSourceField(_RefField):
    def __init__(self, **kwargs):
        kwargs["source"] = "*"
        super().__init__(**kwargs)

    def to_representation(self, obj):
        if not obj.source_file:
            return None
        return {
            "url": absolute_url(obj.source_file.url, self.context.get("request")),
            "size": obj.source_size,
            "ext": _ext(obj.source_file),
        }


@extend_schema_field({
    "type": "string",
    "enum": list(Presentation.CATEGORIES),
    "description": "projects — презентация опубликованного проекта, industry — остальные",
})
class PresentationCategoryField(_RefField):
    def __init__(self, **kwargs):
        kwargs["source"] = "*"
        super().__init__(**kwargs)

    def to_representation(self, obj):
        return obj.category


class PresentationShortSerializer(serializers.ModelSerializer):
    """Элемент списка презентаций внутри проекта (без ссылки на сам проект)."""

    slug = TranslatedField()
    title = TranslatedField()
    excerpt = TranslatedField()
    category = PresentationCategoryField()
    cover = ImageVersionsField()
    sector = SectorField()
    country = CountryShortSerializer(read_only=True, allow_null=True)
    file = PresentationFileField()
    is_translated = IsTranslatedField()

    class Meta:
        model = Presentation
        fields = [
            "id", "slug", "title", "excerpt", "category", "cover", "sector", "country", "file",
            "published_at", "is_translated",
        ]


class PresentationListSerializer(PresentationShortSerializer):
    project = ProjectRefField()

    class Meta(PresentationShortSerializer.Meta):
        fields = [
            "id", "slug", "title", "excerpt", "category", "cover", "sector", "project", "country", "file",
            "published_at", "is_translated",
        ]


class PresentationDetailSerializer(PresentationListSerializer):
    content = HtmlField()
    source_file = PresentationSourceField()
    seo = SeoField(description_field="excerpt", image_field="cover")

    class Meta(PresentationListSerializer.Meta):
        fields = [
            "id",
            "slug",
            "title",
            "excerpt",
            "content",
            "category",
            "cover",
            "sector",
            "project",
            "country",
            "file",
            "source_file",
            "published_at",
            "is_translated",
            "seo",
        ]


class ProjectListSerializer(serializers.ModelSerializer):
    slug = TranslatedField()
    title = TranslatedField()
    excerpt = TranslatedField()
    cover = ImageVersionsField()
    country = CountryShortSerializer(read_only=True)
    is_translated = IsTranslatedField()

    class Meta:
        model = Project
        fields = ["id", "slug", "title", "excerpt", "cover", "country", "published_at", "is_translated"]


class ProjectDetailSerializer(ProjectListSerializer):
    content = HtmlField()
    partners = PartnerSerializer(
        many=True, read_only=True, help_text="Только партнёры с согласием на публикацию"
    )
    gallery = GalleryImageSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    presentations = PresentationShortSerializer(
        many=True, read_only=True, help_text="Опубликованные и переведённые на `lang` презентации проекта"
    )
    seo = SeoField(description_field="excerpt", image_field="cover")

    class Meta(ProjectListSerializer.Meta):
        fields = [
            "id",
            "slug",
            "title",
            "excerpt",
            "content",
            "cover",
            "country",
            "published_at",
            "partners",
            "gallery",
            "attachments",
            "presentations",
            "is_translated",
            "seo",
        ]
