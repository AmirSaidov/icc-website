"""Валидация формы обращения — ровно по таблице SPEC.md, 5.1."""
import re

from django.core.validators import RegexValidator
from rest_framework import serializers

from .models import Feedback

# \r, \n и прочие разрывы строк, которые почтовые клиенты могут счесть концом заголовка
LINE_BREAKS = re.compile(r"[\r\n  \x0b\x0c\x85]+")


def single_line(value):
    """Убирает переводы строк: значение попадает в тему письма (защита от инъекции в заголовки)."""
    return " ".join(LINE_BREAKS.sub(" ", value).split())


class FeedbackSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(choices=Feedback.Type.choices)
    full_name = serializers.CharField(min_length=2, max_length=150)
    company = serializers.CharField(max_length=200)
    country = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(
        max_length=30,
        required=False,
        allow_blank=True,
        allow_null=True,
        validators=[RegexValidator(r"^[\d\s+\-()]*$", "Допустимы только цифры, +, пробелы, - и ().")],
    )
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField(min_length=10, max_length=5000)
    consent = serializers.BooleanField(help_text="Только true")
    lang = serializers.ChoiceField(choices=Feedback.Lang.choices)
    website = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
        help_text="Honeypot: скрытое поле, человек его не заполняет. Должно быть пустым.",
    )

    class Meta:
        model = Feedback
        fields = [
            "type", "full_name", "company", "country", "email", "phone",
            "subject", "message", "consent", "lang", "website",
        ]

    def validate_full_name(self, value):
        value = single_line(value)
        if len(value) < 2:
            raise serializers.ValidationError("Убедитесь, что это значение содержит не менее 2 символов.")
        return value

    def validate_subject(self, value):
        value = single_line(value)
        if not value:
            raise serializers.ValidationError("Это поле не может быть пустым.")
        return value

    def validate_phone(self, value):
        return value or None

    def validate_consent(self, value):
        if value is not True:
            raise serializers.ValidationError("Необходимо согласие на обработку персональных данных.")
        return value

    def create(self, validated_data):
        validated_data.pop("website", None)
        return super().create(validated_data)


class FeedbackCreatedSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=True)
