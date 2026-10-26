from modeltranslation.translator import TranslationOptions, register

from apps.core.models import SEO_TRANSLATED_FIELDS

from .models import Country, Partner, Presentation, Project, Sector


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


@register(Sector)
class SectorTranslationOptions(TranslationOptions):
    fields = ("name", "slug")
    empty_values = {"slug": None}


@register(Presentation)
class PresentationTranslationOptions(TranslationOptions):
    fields = ("title", "slug", "description", *SEO_TRANSLATED_FIELDS)
    empty_values = {"slug": None}
