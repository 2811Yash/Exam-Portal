from django.urls import path
from django.contrib.auth import views as auth_views
from .views import signup,dashboard,take_exam,submit_exam,exam_results ,login_view,signup_view,logout_view,exam_submission_confirmation

urlpatterns = [
    path('', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
]
urlpatterns += [
    path('dashboard', dashboard, name='dashboard'),
]

urlpatterns += [
    path('exam/<int:exam_id>/', take_exam, name='take_exam'),
    path('exam/<int:exam_id>/submit/', submit_exam, name='submit_exam'),
]

urlpatterns += [
    path("exam/submitted/", exam_submission_confirmation, name="exam_submission_confirmation"),

]


 