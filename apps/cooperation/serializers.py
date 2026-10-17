from rest_framework import serializers

from apps.core.serializers import (
    AttachmentSerializer,
    GalleryImageSerializer,
    ImageVersionsField,
    IsTranslatedField,
    NullableCharField,
    SeoField,
    TranslatedField,
)

from .models import Country, Partner, Project


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
    content = TranslatedField(help_text="Безопасный HTML (очищен при сохранении)")
    partners = PartnerSerializer(
        many=True, read_only=True, help_text="Только партнёры с согласием на публикацию"
    )
    gallery = GalleryImageSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
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
            "is_translated",
            "seo",
        ]
