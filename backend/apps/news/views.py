from django.utils import timezone
from rest_framework import generics

from apps.core.api import (
    LangMixin,
    SlugDetailAPIView,
    StandardPagination,
    TranslatedListAPIView,
    gallery_and_attachments_prefetch,
    get_choice_param,
)
from apps.core.i18n import any_slug_q
from apps.core.schema import SLUG_PATH_PARAMETER, api_doc, query_param

from .models import Event, News, NewsCategory
from .serializers import (
    EventDetailSerializer,
    EventListSerializer,
    EventTypeSerializer,
    NewsCategorySerializer,
    NewsDetailSerializer,
    NewsListSerializer,
)

TAGS = ["Новости и мероприятия"]

EVENT_WHEN = ("upcoming", "past")


@api_doc(
    summary="Категории новостей",
    serializer=NewsCategorySerializer,
    tags=TAGS,
    example="news_categories",
    is_list=True,
)
class NewsCategoryListView(TranslatedListAPIView):
    queryset = NewsCategory.objects.all()
    serializer_class = NewsCategorySerializer


@api_doc(
    summary="Новости",
    description="Опубликованные и переведённые на `lang` новости, свежие сверху (по `published_at`).",
    serializer=NewsListSerializer,
    tags=TAGS,
    example="news_list",
    is_list=True,
    parameters=[query_param("category", "slug категории на любом языке")],
)
class NewsListView(TranslatedListAPIView):
    queryset = News.objects.select_related("category").order_by("-published_at", "-id")
    serializer_class = NewsListSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get("category")
        if category:
            category_ids = NewsCategory.objects.filter(any_slug_q(category)).values("id")
            queryset = queryset.filter(category__in=category_ids)
        return queryset


@api_doc(
    summary="Новость",
    description="Поиск по slug на любом языке. Без перевода на `lang` — 200, "
    "переводимые поля null, `is_translated: false`.",
    serializer=NewsDetailSerializer,
    tags=TAGS,
    example="news_detail",
    detail=True,
    parameters=[SLUG_PATH_PARAMETER],
)
class NewsDetailView(SlugDetailAPIView):
    queryset = News.objects.select_related("category")
    serializer_class = NewsDetailSerializer

    def get_queryset(self):
        return super().get_queryset().prefetch_related(*gallery_and_attachments_prefetch(self.lang))


@api_doc(
    summary="Мероприятия",
    description="`when=upcoming` — по `start_at` по возрастанию; `when=past` — по `start_at` "
    "по убыванию; без `when` — все, по убыванию. Предстоящее/прошедшее определяется по "
    "`end_at` (если пусто — по `start_at`).",
    serializer=EventListSerializer,
    tags=TAGS,
    example="events_list",
    is_list=True,
    parameters=[
        query_param("when", "Предстоящие или прошедшие", enum=list(EVENT_WHEN)),
        query_param("type", "Тип мероприятия", enum=list(Event.Type.values)),
    ],
)
class EventListView(TranslatedListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventListSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        when = get_choice_param(self.request, "when", EVENT_WHEN)
        event_type = get_choice_param(self.request, "type", Event.Type.values)
        if event_type:
            queryset = queryset.filter(type=event_type)
        upcoming = Event.upcoming_q(timezone.now())
        if when == "upcoming":
            return queryset.filter(upcoming).order_by("start_at", "id")
        if when == "past":
            return queryset.exclude(upcoming).order_by("-start_at", "-id")
        return queryset.order_by("-start_at", "-id")


@api_doc(
    summary="Мероприятие",
    description="Поиск по slug на любом языке. Без перевода на `lang` — 200, "
    "переводимые поля null, `is_translated: false`.",
    serializer=EventDetailSerializer,
    tags=TAGS,
    example="event_detail",
    detail=True,
    parameters=[SLUG_PATH_PARAMETER],
)
class EventDetailView(SlugDetailAPIView):
    queryset = Event.objects.all()
    serializer_class = EventDetailSerializer

    def get_queryset(self):
        return super().get_queryset().prefetch_related(*gallery_and_attachments_prefetch(self.lang))


@api_doc(
    summary="Типы мероприятий",
    description="Коды типов с подписями на языке запроса — для фильтра `type`.",
    serializer=EventTypeSerializer,
    tags=TAGS,
    example="event_types",
    is_list=True,
)
class EventTypeListView(LangMixin, generics.ListAPIView):
    serializer_class = EventTypeSerializer
    pagination_class = None

    def get_queryset(self):
        return [{"code": code, "label": Event.type_label(code, self.lang)} for code in Event.Type.values]
