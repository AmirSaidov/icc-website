"""
Помощник для тестов админки: собирает POST-данные из отрендеренной формы так,
как их отправил бы браузер (основная форма + inline-формсеты + management forms).
"""
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.forms import CheckboxInput, FileInput, MultiWidget

from apps.core.admin_forms import JsonRowsWidget


def _field_items(bound):
    widget = bound.field.widget
    if isinstance(widget, RelatedFieldWidgetWrapper):
        widget = widget.widget
    name, value = bound.html_name, bound.value()
    if isinstance(widget, FileInput):
        return []
    if isinstance(widget, CheckboxInput):
        return [(name, "on")] if value else []
    if isinstance(widget, JsonRowsWidget):
        rows = value or []
        items = [(f"{name}-count", str(len(rows)))]
        for index, row in enumerate(rows):
            items += [(f"{name}-{index}-{key}", row.get(key, "")) for key, _ in widget.columns]
        return items
    context = widget.get_context(name, value, {})["widget"]
    if isinstance(widget, MultiWidget):
        return [(sub["name"], sub["value"] or "") for sub in context["subwidgets"]]
    value = context["value"]
    if isinstance(value, list):
        return [(name, item) for item in value if item not in ("", None)] or [(name, "")]
    return [(name, "" if value is None else value)]


def _form_items(form):
    items = []
    for bound in form:
        items += _field_items(bound)
    return items


def form_data(response):
    """POST-данные формы добавления/изменения объекта в админке."""
    items = _form_items(response.context["adminform"].form)
    for inline in response.context["inline_admin_formsets"]:
        formset = inline.formset
        items += _form_items(formset.management_form)
        for form in formset.forms:
            items += _form_items(form)
    data = {}
    for key, value in items:
        data.setdefault(key, []).append(value)
    return {key: values if len(values) > 1 else values[0] for key, values in data.items()}


def changelist_data(response):
    """POST-данные формы list_editable на странице списка."""
    formset = response.context["cl"].formset
    data = dict(_form_items(formset.management_form))
    for form in formset.forms:
        data.update(dict(_form_items(form)))
    return data
