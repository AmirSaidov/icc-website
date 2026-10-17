from modeltranslation.translator import TranslationOptions, register

from apps.core.models import SEO_TRANSLATED_FIELDS

from .models import Direction, HomeBlock, Page, Service


@register(Page)
class PageTranslationOptions(TranslationOptions):
    fields = ("title", "slug", "content", *SEO_TRANSLATED_FIELDS)
    empty_values = {"slug": None}


@register(HomeBlock)
class HomeBlockTranslationOptions(TranslationOptions):
    fields = ("title", "text", "button_text")


@register(Direction)
class DirectionTranslationOptions(TranslationOptions):
    fields = ("title", "slug", "short_text", "content", *SEO_TRANSLATED_FIELDS)
    empty_values = {"slug": None}


@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = (
        "title",
        "slug",
        "short_text",
        "content",
        "how_to_apply",
        "contact_person",
        *SEO_TRANSLATED_FIELDS,
    )
    empty_values = {"slug": None}
