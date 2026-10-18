"""
Поле админки для JSON-списков (ContactInfo.phones / socials): таблица строк
с обычными полями ввода вместо сырого JSON. Без JS и сторонних зависимостей.
"""
import json
import re

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.html import format_html, format_html_join

EXTRA_ROWS = 3


class JsonRowsWidget(forms.Widget):
    def __init__(self, columns, attrs=None):
        self.columns = columns  # [(ключ, заголовок)]
        super().__init__(attrs)

    def value_from_datadict(self, data, files, name):
        count = int(data.get(f"{name}-count") or 0)
        rows = []
        for index in range(count):
            row = {key: (data.get(f"{name}-{index}-{key}") or "").strip() for key, _ in self.columns}
            if any(row.values()):
                rows.append(row)
        return rows

    def render(self, name, value, attrs=None, renderer=None):
        if isinstance(value, str):
            value = json.loads(value or "[]")
        rows = list(value or []) + [{}] * EXTRA_ROWS
        header = format_html_join("", "<th>{}</th>", ((title,) for _, title in self.columns))
        body = format_html_join(
            "",
            "<tr>{}</tr>",
            (
                (
                    format_html_join(
                        "",
                        '<td><input type="text" name="{}-{}-{}" value="{}" class="vTextField"></td>',
                        ((name, index, key, row.get(key, "")) for key, _ in self.columns),
                    ),
                )
                for index, row in enumerate(rows)
            ),
        )
        return format_html(
            '<table class="json-rows"><thead><tr>{}</tr></thead><tbody>{}</tbody></table>'
            '<input type="hidden" name="{}-count" value="{}">',
            header,
            body,
            name,
            len(rows),
        )


class JsonRowsField(forms.Field):
    """columns: [(ключ, заголовок)]; required: ключи, обязательные в непустой строке."""

    def __init__(self, columns, required_keys=(), row_validators=None, **kwargs):
        self.columns = columns
        self.required_keys = required_keys
        self.row_validators = row_validators or {}
        kwargs.setdefault("required", False)
        kwargs["widget"] = JsonRowsWidget(columns)
        super().__init__(**kwargs)

    def clean(self, value):
        rows = value or []
        errors = []
        titles = dict(self.columns)
        for number, row in enumerate(rows, start=1):
            for key in self.required_keys:
                if not row.get(key):
                    errors.append(f"Строка {number}: заполните «{titles[key]}».")
            for key, validator in self.row_validators.items():
                if row.get(key):
                    try:
                        validator(row[key])
                    except ValidationError as error:
                        errors.extend(f"Строка {number}, «{titles[key]}»: {m}" for m in error.messages)
        if errors:
            raise ValidationError(errors)
        return [{key: row.get(key, "") for key, _ in self.columns} for row in rows]


def validate_phone(value):
    if not re.fullmatch(r"[\d\s+\-()]{3,30}", value):
        raise ValidationError("Только цифры, +, пробелы, -, (), до 30 символов.")


def validate_social_type(value):
    if not re.fullmatch(r"[a-z0-9_-]+", value):
        raise ValidationError("Латиница в нижнем регистре, например telegram.")


def phones_field():
    return JsonRowsField(
        columns=[
            ("label_ru", "Подпись (RU)"),
            ("label_en", "Подпись (EN)"),
            ("label_zh", "Подпись (中文)"),
            ("number", "Номер"),
        ],
        required_keys=("number",),
        row_validators={"number": validate_phone},
        label="Телефоны",
        help_text="Пустые строки не сохраняются. Нужно больше строк — сохраните, появятся новые.",
    )


def socials_field():
    return JsonRowsField(
        columns=[("type", "Тип (telegram, facebook, ...)"), ("url", "Ссылка")],
        required_keys=("type", "url"),
        row_validators={"type": validate_social_type, "url": URLValidator()},
        label="Соцсети",
        help_text="Тип — ключ иконки на фронте. Нужно больше строк — сохраните, появятся новые.",
    )
