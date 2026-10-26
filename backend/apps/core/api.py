"""Общие классы публичного API: язык, публикация, переводы, пагинация, поиск по slug."""
from django.db.models import Prefetch
from django.utils import timezone
from rest_framework import generics
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.pagination import PageNumberPagination

from .i18n import DEFAULT_LANG, find_by_any_slug, get_request_lang, has_field, translated_q
from .models import Attachment, PublishableModel


class StandardPagination(PageNumberPagination):
    """page / page_size: по умолчанию 9, максимум 50 (SPEC.md, 3.1)."""

    page_size = 9
    page_size_query_param = "page_size"
    max_page_size = 50


def published(queryset):
    """
    Опубликованные записи. У моделей с published_at (News, Project) ещё и отложенная
    публикация: запись с датой в будущем скрыта до её наступления (SPEC.md, 2.4).
    """
    queryset = queryset.filter(status=PublishableModel.Status.PUBLISHED)
    if has_field(queryset.model, "published_at"):
        queryset = queryset.filter(published_at__lte=timezone.now())
    return queryset


def is_published(obj):
    """То же правило, что published(), но для объекта в памяти (вложенные ссылки в ответах)."""
    if obj.status != PublishableModel.Status.PUBLISHED:
        return False
    published_at = getattr(obj, "published_at", None)
    return published_at is None or published_at <= timezone.now()


def gallery_and_attachments_prefetch(lang):
    """Для News / Event / Project: галерея целиком, вложения — только переведённые на lang."""
    return (
        "gallery",
        Prefetch("attachments", queryset=Attachment.objects.filter(translated_q(Attachment, lang))),
    )


def get_choice_param(request, name, choices):
    """Необязательный query-параметр с фиксированным набором значений; неизвестное → 400."""
    value = request.query_params.get(name)
    if value in (None, ""):
        return None
    if value not in choices:
        raise ValidationError(
            {name: [f"Недопустимое значение «{value}». Допустимо: {', '.join(choices)}."]}
        )
    return value


class LangMixin:
    """
    Единая обработка ?lang=ru|en|zh для всех вьюх: валидирует параметр
    (невалидный → 400) и передаёт язык в контекст сериализатора.
    """

    lang = DEFAULT_LANG

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.lang = get_request_lang(request)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["lang"] = self.lang
        return context


class TranslatedListAPIView(LangMixin, generics.ListAPIView):
    """Список: только опубликованные (если у модели есть status) и переведённые на язык запроса."""

    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        model = queryset.model
        if has_field(model, "status"):
            queryset = published(queryset)
        return queryset.filter(translated_q(model, self.lang))


class SlugDetailAPIView(LangMixin, generics.RetrieveAPIView):
    """
    Детальный ответ: только опубликованные, поиск по slug на любом из трёх языков.
    Если перевода на язык запроса нет — 200 с null-полями и is_translated: false.
    """

    lookup_url_kwarg = "slug"

    def get_queryset(self):
        return published(super().get_queryset())

    def get_object(self):
        obj = find_by_any_slug(self.get_queryset(), self.kwargs[self.lookup_url_kwarg], self.lang)
        if obj is None:
            raise NotFound()
        return obj
