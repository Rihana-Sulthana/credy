from .models import UserRequestCount
from django.utils.deprecation import MiddlewareMixin
from rest_framework_jwt import authentication


class RequestCountMiddleware(MiddlewareMixin):

    def process_request(self, request):
        try:
            if not "request-count" in request.path:
                request.user = authentication.JSONWebTokenAuthentication().authenticate(request)[0]
                request_count = UserRequestCount.objects.filter(user_id=request.user.id).first()
                if request_count:
                    request_count.request_count += 1
                    request_count.save()
                else:
                    request_count = UserRequestCount.objects.create(user_id=request.user.id,
                                                                    request_count=1)
            return None
        except:
            pass
