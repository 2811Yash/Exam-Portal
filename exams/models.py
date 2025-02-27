from django.db import models
from django.contrib.auth.models import User
from admin_panel.models import Exam, Question

class Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=100)
    is_correct = models.BooleanField()

    def __str__(self):
        return f"{self.user} - {self.exam}"


