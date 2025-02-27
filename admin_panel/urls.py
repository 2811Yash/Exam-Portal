from django.urls import path
from . import views

urlpatterns = [
    path('add_question/', views.add_question, name='add_question'),
    path("admin-login/", views.admin_login, name="admin_login"),
    path("admin-logout/", views.admin_logout, name="admin_logout"),
    path("", views.admin_dashboard, name="admin_dashboard"),
    path('add_exam/', views.add_exam, name='add_exam'),
    path('exam_list/', views.exam_list, name='exam_list'),
    path("staff_signup/", views.staff_signup, name="staff_signup"),
    path("results/",views.results,name="results"),
    path("delete_exam/", views.delete_exam, name="delete_exam"),
    

    
]