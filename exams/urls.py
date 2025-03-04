from django.urls import path
from django.contrib.auth import views as auth_views
from .views import dashboard,take_exam,submit_exam ,login_view,logout_view,exam_submission_confirmation

urlpatterns = [
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard', dashboard, name='dashboard'),
    path('exam/<int:exam_id>/', take_exam, name='take_exam'),
    path('exam/<int:exam_id>/submit/', submit_exam, name='submit_exam'),
    path("exam/submitted/", exam_submission_confirmation, name="exam_submission_confirmation"),
]



 