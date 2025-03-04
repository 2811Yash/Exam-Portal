from django.urls import path
from . import views

urlpatterns = [
    path("admin-login/", views.admin_login, name="admin_login"),
    path("admin-logout/", views.admin_logout, name="admin_logout"),
    path("", views.admin_dashboard, name="admin_dashboard"),
    path('exam_list/', views.exam_list, name='exam_list'),
    path("staff_signup/", views.staff_signup, name="staff_signup"),
    path("results/",views.results,name="results"),
    path("delete_exam/", views.delete_exam, name="delete_exam"),
    path("add-exam/", views.add_exam, name="add_exam"),
    path("add-question/<int:exam_id>/", views.add_question, name="add_question"),  # Accepts exam_id
    path("questions/<int:exam_id>/", views.question_list, name="question_list"),
    path("delete-question/<int:question_id>/",views.delete_question, name="delete_question"),
    path("add_student/", views.add_student, name="add_student"),
    path("exam-results/<int:exam_id>/", views.exam_results, name="exam_results"),
    path("student_list/", views.student_list, name="student_list"),

    
]