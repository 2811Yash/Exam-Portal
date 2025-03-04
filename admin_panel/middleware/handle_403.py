from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

class Handle403Middleware(MiddlewareMixin):
    def process_response(self, request, response):
        if response.status_code == 403:
            return redirect('admin-panel/')  # Redirect to login page
        return response
