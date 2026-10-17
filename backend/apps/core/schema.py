"""
Описание эндпоинтов для drf-spectacular: параметр lang, фильтры, примеры ответов.

Примеры — реальные ответы API на seed-данных, лежат в apps/core/api_examples/*.json
и пересобираются командой `python manage.py export_api_examples`.
"""
import json
from pathlib import Path

from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import serializers

from .i18n import DEFAULT_LANG, LANGS

EXAMPLES_DIR = Path(__file__).resolve().parent / "api_examples"

LANG_PARAMETER = OpenApiParameter(
    name="lang",
    type=str,
    location=OpenApiParameter.QUERY,
    required=False,
    enum=list(LANGS),
    default=DEFAULT_LANG,
    description="Язык ответа. По умолчанию ru. Невалидное значение → 400 "
    '`{"lang": ["..."]}`.',
)


def query_param(name, description, enum=None):
    return OpenApiParameter(
        name=name,
        type=str,
        location=OpenApiParameter.QUERY,
        required=False,
        enum=enum,
        description=description,
    )


def path_param(name, description):
    return OpenApiParameter(
        name=name, type=str, location=OpenApiParameter.PATH, description=description
    )


SLUG_PATH_PARAMETER = path_param(
    "slug", "slug записи на любом из трёх языков (ru, en или zh)"
)


class ValidationErrorSerializer(serializers.Serializer):
    lang = serializers.ListField(child=serializers.CharField(), required=False)


class DetailErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()


ERROR_400 = OpenApiResponse(
    ValidationErrorSerializer,
    description='Невалидный параметр: `{"<параметр>": ["ошибка"]}`',
)
ERROR_404 = OpenApiResponse(DetailErrorSerializer, description="Запись не найдена или не опубликована")


def load_example(name):
    path = EXAMPLES_DIR / f"{name}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _list_item(value):
    """Для списков spectacular сам оборачивает пример в массив / пагинацию — отдаём один элемент."""
    if isinstance(value, dict) and "results" in value:
        value = value["results"]
    if isinstance(value, list):
        return value[0] if value else None
    return value


def api_doc(*, summary, serializer, tags, example=None, is_list=False, detail=False,
            parameters=(), description=None):
    """extend_schema для публичного GET-эндпоинта: lang + фильтры + пример + коды ошибок."""
    examples = []
    value = load_example(example) if example else None
    if value is not None and is_list:
        value = _list_item(value)
    if value is not None:
        examples.append(
            OpenApiExample("Пример (seed-данные)", value=value, response_only=True, status_codes=["200"])
        )
    responses = {200: serializer, 400: ERROR_400}
    if detail:
        responses[404] = ERROR_404
    return extend_schema(
        summary=summary,
        description=description,
        tags=tags,
        parameters=[LANG_PARAMETER, *parameters],
        responses=responses,
        examples=examples,
    )
