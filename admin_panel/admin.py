import admin_panel.models
from django.contrib import admin
from .models import Exam, Question,ExamResult,ExamAttempt

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_time', 'duration']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'exam', 'correct_answer']


class ExamResultAdmin(admin.ModelAdmin):
    list_display = ["user", "exam", "score"]

admin.site.register(ExamResult, ExamResultAdmin)

@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'exam', 'total_time_taken','start_time','end_time']

