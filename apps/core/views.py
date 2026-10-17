from rest_framework import generics

from .api import LangMixin, TranslatedListAPIView
from .models import Attachment, ContactInfo, SiteSettings
from .schema import api_doc
from .serializers import AttachmentSerializer, ContactInfoSerializer, SiteSettingsPublicSerializer

TAGS = ["Справочная информация"]


@api_doc(
    summary="Контакты",
    serializer=ContactInfoSerializer,
    tags=TAGS,
    example="contacts",
)
class ContactInfoView(LangMixin, generics.RetrieveAPIView):
    serializer_class = ContactInfoSerializer

    def get_object(self):
        return ContactInfo.load()


@api_doc(
    summary="Публичные настройки сайта",
    serializer=SiteSettingsPublicSerializer,
    tags=TAGS,
    example="settings",
)
class SiteSettingsView(LangMixin, generics.RetrieveAPIView):
    serializer_class = SiteSettingsPublicSerializer

    def get_object(self):
        return SiteSettings.load()


@api_doc(
    summary="Документы",
    description="Документы с `show_in_documents=True`, переведённые на `lang`, по `order`.",
    serializer=AttachmentSerializer,
    tags=TAGS,
    example="documents",
    is_list=True,
)
class DocumentListView(TranslatedListAPIView):
    queryset = Attachment.objects.filter(show_in_documents=True).order_by("order", "id")
    serializer_class = AttachmentSerializer
