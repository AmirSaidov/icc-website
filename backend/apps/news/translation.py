from modeltranslation.translator import TranslationOptions, register

from apps.core.models import SEO_TRANSLATED_FIELDS

from .models import Event, News, NewsCategory


@register(NewsCategory)
class NewsCategoryTranslationOptions(TranslationOptions):
    fields = ("name", "slug")
    empty_values = {"slug": None}


@register(News)
class NewsTranslationOptions(TranslationOptions):
    fields = ("title", "slug", "excerpt", "content", *SEO_TRANSLATED_FIELDS)
    empty_values = {"slug": None}


@register(Event)
class EventTranslationOptions(TranslationOptions):
    fields = ("title", "slug", "location", "excerpt", "content", *SEO_TRANSLATED_FIELDS)
    empty_values = {"slug": None}
