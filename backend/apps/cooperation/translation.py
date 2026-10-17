from modeltranslation.translator import TranslationOptions, register

from apps.core.models import SEO_TRANSLATED_FIELDS

from .models import Country, Partner, Project


@register(Country)
class CountryTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(Partner)
class PartnerTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = ("title", "slug", "excerpt", "content", *SEO_TRANSLATED_FIELDS)
    empty_values = {"slug": None}
