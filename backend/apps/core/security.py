"""Логирование событий безопасности: блокировки входа (django-axes)."""
import logging

from axes.signals import user_locked_out
from django.dispatch import receiver

logger = logging.getLogger("apps.core.security")


@receiver(user_locked_out)
def log_lockout(sender, request, username, ip_address, **kwargs):
    logger.warning("Вход заблокирован после неудачных попыток: username=%r, ip=%s", username, ip_address)
