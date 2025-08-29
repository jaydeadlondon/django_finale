from django.http import JsonResponse
from django.core.cache import cache
import time


class ThrottlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_limit = 10
        self.time_window = 60

    def __call__(self, request):
        ip_address = self.get_client_ip(request)

        cache_key = f'throttle_{ip_address}'

        request_history = cache.get(cache_key, [])

        now = time.time()

        request_history = [
            timestamp for timestamp in request_history
            if now - timestamp < self.time_window
        ]

        if len(request_history) >= self.requests_limit:
            oldest_request = min(request_history)
            retry_after = int(self.time_window - (now - oldest_request))

            return JsonResponse({
                'error': 'Превышен лимит запросов',
                'message': f'Вы превысили лимит в {self.requests_limit} запросов за {self.time_window} секунд.',
                'retry_after': f'{retry_after} секунд'
            }, status=429)

        request_history.append(now)

        cache.set(cache_key, request_history, self.time_window)

        response = self.get_response(request)

        response['X-RateLimit-Limit'] = str(self.requests_limit)
        response['X-RateLimit-Remaining'] = str(self.requests_limit - len(request_history))
        response['X-RateLimit-Reset'] = str(int(now + self.time_window))

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip