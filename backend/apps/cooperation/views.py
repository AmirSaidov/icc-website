from django.db.models import Prefetch, Q

from apps.core.api import (
    SlugDetailAPIView,
    StandardPagination,
    TranslatedListAPIView,
    gallery_and_attachments_prefetch,
    get_choice_param,
    published,
)
from apps.core.i18n import any_slug_q, translated_q
from apps.core.schema import SLUG_PATH_PARAMETER, api_doc, query_param

from .models import Country, Partner, Presentation, Project, Sector
from .serializers import (
    CountrySerializer,
    PartnerSerializer,
    PresentationDetailSerializer,
    PresentationListSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
    SectorSerializer,
)

TAGS = ["Международное сотрудничество"]
PRESENTATION_TAGS = ["Презентации"]

COUNTRY_PARAMETER = query_param("country", "Код страны ISO 3166-1 alpha-2, например CN")


def get_country_code(request):
    code = request.query_params.get("country")
    return code.upper() if code else None


def project_presentations(lang):
    """Презентации внутри проекта: опубликованные (с учётом published_at), переведённые на lang, по order."""
    return (
        published(Presentation.objects.filter(translated_q(Presentation, lang)))
        .select_related("sector", "country")
        .order_by("order", "-published_at", "-id")
    )


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
                Prefetch("presentations", queryset=project_presentations(self.lang)),
                *gallery_and_attachments_prefetch(self.lang),
            )
        )


@api_doc(
    summary="Сферы презентаций",
    description="Сферы, переведённые на `lang`, по порядку — для фильтра `sector`.",
    serializer=SectorSerializer,
    tags=PRESENTATION_TAGS,
    example="sectors",
    is_list=True,
)
class SectorListView(TranslatedListAPIView):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer


@api_doc(
    summary="Презентации",
    description="Опубликованные и переведённые на `lang` презентации, свежие сверху (по `published_at`). "
    "`category=projects` — презентации опубликованных проектов, `industry` — остальные; другое "
    "значение → 400. Неизвестные `sector` / `project` / `country` → пустой список.",
    serializer=PresentationListSerializer,
    tags=PRESENTATION_TAGS,
    example="presentations_list",
    is_list=True,
    parameters=[
        query_param("category", "Раздел: projects или industry", enum=list(Presentation.CATEGORIES)),
        query_param("sector", "slug сферы на любом языке"),
        query_param("project", "slug проекта на любом языке"),
        COUNTRY_PARAMETER,
    ],
)
class PresentationListView(TranslatedListAPIView):
    queryset = Presentation.objects.select_related("sector", "project", "country").order_by(
        "-published_at", "-id"
    )
    serializer_class = PresentationListSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        category = get_choice_param(self.request, "category", Presentation.CATEGORIES)
        if category:
            # то же правило, что у поля category: проект есть и опубликован
            with_project = Q(project__in=published(Project.objects.all()).values("id"))
            queryset = queryset.filter(with_project if category == Presentation.CATEGORY_PROJECTS else ~with_project)
        if params.get("sector"):
            sectors = Sector.objects.filter(any_slug_q(params["sector"]))
            queryset = queryset.filter(sector__in=sectors.values("id"))
        if params.get("project"):
            # только опубликованные проекты: по slug черновика связь не раскрываем
            projects = published(Project.objects.filter(any_slug_q(params["project"])))
            queryset = queryset.filter(project__in=projects.values("id"))
        code = get_country_code(self.request)
        if code:
            queryset = queryset.filter(country__code=code)
        return queryset


@api_doc(
    summary="Презентация",
    description="`file` — PDF для просмотра на сайте (iframe или pdf.js), `source_file` — PPTX "
    "только для скачивания или null. Поиск по slug на любом языке. Без перевода на `lang` — 200, "
    "переводимые поля null, `is_translated: false`.",
    serializer=PresentationDetailSerializer,
    tags=PRESENTATION_TAGS,
    example="presentation_detail",
    detail=True,
    parameters=[SLUG_PATH_PARAMETER],
)
class PresentationDetailView(SlugDetailAPIView):
    queryset = Presentation.objects.select_related("sector", "project", "country")
    serializer_class = PresentationDetailSerializer
