"""Письмо о новом обращении (SPEC.md, 5.1)."""
import logging
import re

from django.conf import settings
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils import timezone

from apps.core.models import SiteSettings

from .models import Feedback

logger = logging.getLogger("apps.feedback")


def get_recipients():
    """SiteSettings.feedback_emails, если пусто — FEEDBACK_EMAIL из .env."""
    raw = SiteSettings.load().feedback_emails or settings.FEEDBACK_EMAIL
    return [address for address in re.split(r"[,;\s]+", raw or "") if address]


def build_message(feedback, recipients):
    created = timezone.localtime(feedback.created_at).strftime("%d.%m.%Y %H:%M")
    admin_url = settings.BACKEND_URL + reverse("admin:feedback_feedback_change", args=[feedback.pk])
    lines = [
        f"Новое обращение #{feedback.pk} с сайта ЦПК.",
        "",
        f"Тип: {feedback.get_type_display()}",
        f"ФИО: {feedback.full_name}",
        f"Компания: {feedback.company}",
        f"Страна: {feedback.country}",
        f"Email: {feedback.email}",
        f"Телефон: {feedback.phone or '—'}",
        f"Тема: {feedback.subject}",
        "",
        "Сообщение:",
        feedback.message,
        "",
        f"Язык сайта: {feedback.get_lang_display()}",
        f"Дата: {created}",
        f"IP: {feedback.ip or '—'}",
        "",
        f"Открыть в админке: {admin_url}",
    ]
    return EmailMessage(
        subject=f"[ЦПК] Новое обращение: {feedback.get_type_display()} — {feedback.subject}",
        body="\n".join(lines),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
        reply_to=[feedback.email],
    )


def send_feedback_notification(feedback_id):
    """
    Вызывается через transaction.on_commit. Любая ошибка отправки только пишется в лог:
    обращение уже сохранено, ответ пользователю от почты не зависит.
    """
    try:
        feedback = Feedback.objects.get(pk=feedback_id)
        recipients = get_recipients()
        if not recipients:
            logger.warning(
                "Обращение #%s сохранено, но письмо не отправлено: не заданы получатели "
                "(SiteSettings.feedback_emails и FEEDBACK_EMAIL пусты).",
                feedback_id,
            )
            return
        build_message(feedback, recipients).send()
    except Exception:
        logger.exception("Не удалось отправить письмо об обращении #%s", feedback_id)
