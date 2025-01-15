from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

class LimitSignupByIPMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path == 'accounts/signup/' and request.method == 'POST':
            ip = self.get_client_ip(request)
            signup_attempts = cache.get(ip, 0)
            
            if signup_attempts >= 5:
                return HttpResponseForbidden("Too many signup attempts from this IP address.")
            
            cache.set(ip, signup_attempts + 1, timeout=3600)  # 1 hour timeout

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip