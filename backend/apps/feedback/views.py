from django.db import transaction
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import generics, serializers, status
from rest_framework.exceptions import Throttled
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from apps.core.net import get_client_ip

from .notifications import send_feedback_notification
from .serializers import FeedbackCreatedSerializer, FeedbackSerializer

REQUEST_EXAMPLE = {
    "type": "cooperation",
    "full_name": "Асель Токтогулова",
    "company": "ОсОО «Ала-Тоо Текстиль»",
    "country": "Кыргызстан",
    "email": "asel@example.kg",
    "phone": "+996 555 123 456",
    "subject": "Поиск партнёра в Китае",
    "message": "Ищем производителя оборудования для швейного цеха.",
    "consent": True,
    "lang": "ru",
    "website": "",
}


class FeedbackThrottled(Throttled):
    # у DRF сообщение 429 переведено на русский лишь наполовину
    default_detail = "Слишком много обращений с вашего адреса."
    extra_detail_singular = extra_detail_plural = "Попробуйте снова через {wait} с."


class FieldErrorsSerializer(serializers.Serializer):
    field = serializers.ListField(
        child=serializers.CharField(), help_text="Ключ — имя поля с ошибкой, значение — список сообщений"
    )


class DetailSerializer(serializers.Serializer):
    detail = serializers.CharField()


@extend_schema(
    summary="Отправить обращение",
    description=(
        "Форма «Контакты» / «Сотрудничество». Без авторизации и CSRF. Лимит — 5 запросов в час "
        "с одного IP (считаются все POST, включая невалидные), 6-й → 429. Поле `website` — "
        "honeypot: если заполнено, ответ тоже 201, но обращение не сохраняется."
    ),
    tags=["Формы"],
    request=FeedbackSerializer,
    responses={
        201: FeedbackCreatedSerializer,
        400: OpenApiResponse(FieldErrorsSerializer, description='Ошибки по полям: {"<поле>": ["ошибка"]}'),
        429: OpenApiResponse(DetailSerializer, description="Превышен лимит запросов"),
    },
    examples=[
        OpenApiExample("Обращение", value=REQUEST_EXAMPLE, request_only=True),
        OpenApiExample("Успех", value={"ok": True}, response_only=True, status_codes=["201"]),
        OpenApiExample(
            "Ошибки валидации",
            value={
                "email": ["Обязательное поле."],
                "message": ["Убедитесь, что это значение содержит не менее 10 символов."],
                "consent": ["Необходимо согласие на обработку персональных данных."],
            },
            response_only=True,
            status_codes=["400"],
        ),
        OpenApiExample(
            "Лимит",
            value={"detail": "Слишком много обращений с вашего адреса. Попробуйте снова через 3599 с."},
            response_only=True,
            status_codes=["429"],
        ),
    ],
)
class FeedbackCreateView(generics.GenericAPIView):
    # Без SessionAuthentication: фронт шлёт POST с другого origin, без CSRF-токена.
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "feedback"
    serializer_class = FeedbackSerializer

    def throttled(self, request, wait):
        raise FeedbackThrottled(wait)

    def post(self, request, *args, **kwargs):
        # Honeypot проверяем до валидации: боту отвечаем «успехом», ничего не сохраняя.
        if str(request.data.get("website") or "").strip():
            return Response({"ok": True}, status=status.HTTP_201_CREATED)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            feedback = serializer.save(ip=get_client_ip(request))
            transaction.on_commit(lambda: send_feedback_notification(feedback.pk))
        return Response({"ok": True}, status=status.HTTP_201_CREATED)
