from django.conf import settings
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.utils.functional import SimpleLazyObject

def get_user_from_session(request):
    if request.path.startswith('/admin-panel/'):
        return SimpleLazyObject(lambda: getattr(request, '_admin_user', None))
    return SimpleLazyObject(lambda: getattr(request, '_student_user', None))

class SeparateSessionMiddleware(AuthenticationMiddleware):
    def process_request(self, request):
        if request.path.startswith('/admin-panel/'):
            request.session_key = 'admin_session'
        else:
            request.session_key = 'student_session'
