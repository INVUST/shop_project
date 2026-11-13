import time
from django.http import HttpResponse
from django.conf import settings


class ThrottlingMiddleware:
    """Ограничивает частоту запросов от одного IP.

    Если IP делал запрос менее чем RATE_LIMIT_SECONDS секунд назад —
    возвращаем 429 Too Many Requests.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Словарь: {ip: timestamp последнего запроса}
        self.ip_timestamps = {}

    def __call__(self, request):
        ip = self._get_client_ip(request)
        now = time.time()

        last_seen = self.ip_timestamps.get(ip)
        cooldown = getattr(settings, "THROTTLE_COOLDOWN_SECONDS", 1)

        if last_seen is not None and (now - last_seen) < cooldown:
            wait = round(cooldown - (now - last_seen), 2)
            return HttpResponse(
                f"Слишком много запросов. Подождите {wait} сек. и попробуйте снова.",
                status=429,
            )

        self.ip_timestamps[ip] = now
        return self.get_response(request)

    @staticmethod
    def _get_client_ip(request):
        """Определяем IP с учётом прокси."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")