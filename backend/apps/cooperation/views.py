from django.db.models import Prefetch

from apps.core.api import (
    SlugDetailAPIView,
    StandardPagination,
    TranslatedListAPIView,
    gallery_and_attachments_prefetch,
)
from apps.core.i18n import translated_q
from apps.core.schema import SLUG_PATH_PARAMETER, api_doc, query_param

from .models import Country, Partner, Project
from .serializers import (
    CountrySerializer,
    PartnerSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
)

TAGS = ["Международное сотрудничество"]

COUNTRY_PARAMETER = query_param("country", "Код страны ISO 3166-1 alpha-2, например CN")


def get_country_code(request):
    code = request.query_params.get("country")
    return code.upper() if code else None


def public_partners(lang):
    """Партнёры попадают в API, только если consent_to_publish = True (и переведены на lang)."""
    return (
        Partner.objects.filter(consent_to_publish=True)
        .filter(translated_q(Partner, lang))
        .select_related("country")
    )


@api_doc(
    summary="Страны-партнёры",
    description="Активные страны, переведённые на `lang`.",
    serializer=CountrySerializer,
    tags=TAGS,
    example="countries",
    is_list=True,
)
class CountryListView(TranslatedListAPIView):
    queryset = Country.objects.filter(is_active=True)
    serializer_class = CountrySerializer


@api_doc(
    summary="Партнёры",
    description="Только партнёры с согласием на публикацию.",
    serializer=PartnerSerializer,
    tags=TAGS,
    example="partners",
    is_list=True,
    parameters=[COUNTRY_PARAMETER],
)
class PartnerListView(TranslatedListAPIView):
    queryset = Partner.objects.filter(consent_to_publish=True).select_related("country")
    serializer_class = PartnerSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        code = get_country_code(self.request)
        if code:
            queryset = queryset.filter(country__code=code)
        return queryset


@api_doc(
    summary="Международные проекты",
    description="Опубликованные и переведённые на `lang` проекты, свежие сверху (по `published_at`).",
    serializer=ProjectListSerializer,
    tags=TAGS,
    example="projects_list",
    is_list=True,
    parameters=[COUNTRY_PARAMETER],
)
class ProjectListView(TranslatedListAPIView):
    queryset = Project.objects.select_related("country").order_by("-published_at", "-id")
    serializer_class = ProjectListSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        code = get_country_code(self.request)
        if code:
            queryset = queryset.filter(country__code=code)
        return queryset


@api_doc(
    summary="Международный проект",
    description="С партнёрами (только с согласием на публикацию), галереей и документами. "
    "Поиск по slug на любом языке.",
    serializer=ProjectDetailSerializer,
    tags=TAGS,
    example="project_detail",
    detail=True,
    parameters=[SLUG_PATH_PARAMETER],
)
class ProjectDetailView(SlugDetailAPIView):
    queryset = Project.objects.select_related("country")
    serializer_class = ProjectDetailSerializer

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                Prefetch("partners", queryset=public_partners(self.lang)),
                *gallery_and_attachments_prefetch(self.lang),
            )
        )
