from django.utils import timezone
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from apps.core.api import LangMixin, SlugDetailAPIView, TranslatedListAPIView, published
from apps.core.i18n import find_by_any_slug, translated_q
from apps.core.schema import SLUG_PATH_PARAMETER, api_doc, path_param
from apps.core.seo import build_seo
from apps.core.serializers import get_site_settings
from apps.news.models import Event, News

from .models import Direction, HomeBlock, Page, Service
from .serializers import (
    DirectionDetailSerializer,
    DirectionListSerializer,
    HomeSerializer,
    PageDetailSerializer,
    PageMenuSerializer,
    ServiceDetailSerializer,
    ServiceListSerializer,
)

PAGES_TAGS = ["Главная и страницы"]
SECTIONS_TAGS = ["Направления и услуги"]


def published_translated(queryset, lang):
    return published(queryset).filter(translated_q(queryset.model, lang))


@api_doc(
    summary="Главная",
    description="Всё для главной одним запросом: опубликованные блоки (по order), 4 направления, "
    "3 последние новости, 3 ближайших предстоящих мероприятия и seo страницы `home`. "
    "Во всех списках — только записи, переведённые на `lang`.",
    serializer=HomeSerializer,
    tags=PAGES_TAGS,
    example="home",
)
class HomeView(LangMixin, generics.GenericAPIView):
    serializer_class = HomeSerializer

    def get(self, request, *args, **kwargs):
        lang = self.lang
        home_page = published(Page.objects.filter(key="home")).first()
        data = {
            "blocks": published_translated(HomeBlock.objects.all(), lang).order_by("order", "id"),
            "directions": published_translated(Direction.objects.all(), lang).order_by("order", "id")[:4],
            "news": published_translated(News.objects.select_related("category"), lang).order_by(
                "-published_at", "-id"
            )[:3],
            "events": published_translated(Event.objects.all(), lang)
            .filter(Event.upcoming_q(timezone.now()))
            .order_by("start_at", "id")[:3],
        }
        context = self.get_serializer_context()
        data["seo"] = build_seo(home_page, lang, request, get_site_settings(context))
        return Response(HomeSerializer(data, context=context).data)


@api_doc(
    summary="Страницы для меню",
    description="Опубликованные страницы с `show_in_menu=True`, переведённые на `lang`, по `order`.",
    serializer=PageMenuSerializer,
    tags=PAGES_TAGS,
    example="pages_list",
    is_list=True,
)
class PageMenuListView(TranslatedListAPIView):
    queryset = Page.objects.filter(show_in_menu=True).order_by("order", "id")
    serializer_class = PageMenuSerializer


@api_doc(
    summary="Страница",
    description="Сначала ищется по `key` (системные страницы: home, about, cooperation), "
    "затем по slug на любом языке. Без перевода на `lang` — 200, `is_translated: false`.",
    serializer=PageDetailSerializer,
    tags=PAGES_TAGS,
    example="page_detail",
    detail=True,
    parameters=[path_param("key_or_slug", "key системной страницы или slug на любом языке")],
)
class PageDetailView(SlugDetailAPIView):
    queryset = Page.objects.all()
    serializer_class = PageDetailSerializer
    lookup_url_kwarg = "key_or_slug"

    def get_object(self):
        value = self.kwargs[self.lookup_url_kwarg]
        queryset = self.get_queryset()
        obj = queryset.filter(key=value).first() or find_by_any_slug(queryset, value, self.lang)
        if obj is None:
            raise NotFound()
        return obj


@api_doc(
    summary="Направления",
    description="Опубликованные и переведённые на `lang` направления по `order` (без content).",
    serializer=DirectionListSerializer,
    tags=SECTIONS_TAGS,
    example="directions_list",
    is_list=True,
)
class DirectionListView(TranslatedListAPIView):
    queryset = Direction.objects.order_by("order", "id")
    serializer_class = DirectionListSerializer


@api_doc(
    summary="Направление",
    description="Поиск по slug на любом языке.",
    serializer=DirectionDetailSerializer,
    tags=SECTIONS_TAGS,
    example="direction_detail",
    detail=True,
    parameters=[SLUG_PATH_PARAMETER],
)
class DirectionDetailView(SlugDetailAPIView):
    queryset = Direction.objects.all()
    serializer_class = DirectionDetailSerializer


@api_doc(
    summary="Услуги",
    description="Опубликованные и переведённые на `lang` услуги по `order` "
    "(без content, how_to_apply и контактов).",
    serializer=ServiceListSerializer,
    tags=SECTIONS_TAGS,
    example="services_list",
    is_list=True,
)
class ServiceListView(TranslatedListAPIView):
    queryset = Service.objects.order_by("order", "id")
    serializer_class = ServiceListSerializer


@api_doc(
    summary="Услуга",
    description="Полностью, включая how_to_apply и контакты. Поиск по slug на любом языке.",
    serializer=ServiceDetailSerializer,
    tags=SECTIONS_TAGS,
    example="service_detail",
    detail=True,
    parameters=[SLUG_PATH_PARAMETER],
)
class ServiceDetailView(SlugDetailAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceDetailSerializer
