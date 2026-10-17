from modeltranslation.translator import TranslationOptions, register

from .models import Attachment, ContactInfo, GalleryImage


@register(ContactInfo)
class ContactInfoTranslationOptions(TranslationOptions):
    fields = ("official_name", "address", "work_hours")


@register(GalleryImage)
class GalleryImageTranslationOptions(TranslationOptions):
    fields = ("caption",)


@register(Attachment)
class AttachmentTranslationOptions(TranslationOptions):
    fields = ("title",)
