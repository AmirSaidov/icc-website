"""IP клиента с учётом NUM_PROXIES — одна логика для throttling, axes и Feedback.ip."""
import ipaddress

from rest_framework.throttling import BaseThrottle


def get_client_ip(request):
    """
    То же, что использует DRF throttling (BaseThrottle.get_ident): при NUM_PROXIES=0 —
    REMOTE_ADDR; при NUM_PROXIES=N — N-й адрес с конца X-Forwarded-For (его добавил наш
    ближайший доверенный прокси, подделать его клиент не может).
    Возвращает None, если адрес невалиден.
    """
    ident = BaseThrottle().get_ident(request)
    try:
        return str(ipaddress.ip_address(ident.strip()))
    except (AttributeError, ValueError):
        return None
