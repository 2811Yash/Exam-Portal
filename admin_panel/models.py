from django.db import models
from django.contrib.auth.models import User
from datetime import datetime,timedelta

class Exam(models.Model):
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    duration = models.IntegerField(help_text="Duration in minutes")  # In minutes

    def __str__(self):
        return self.title

    @property
    def end_time(self):
        """Calculate end time based on start_time + duration."""
        return self.start_time + timedelta(minutes=self.duration)

    def is_active(self):
        """Check if the exam is currently ongoing."""
        return self.start_time <= datetime.now() <= self.end_time

class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    text = models.TextField()
    options = models.JSONField()
    correct_answer = models.CharField(max_length=100)

    def __str__(self):
        return self.text
    
class ExamResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    score = models.IntegerField(default=0) 

    def __str__(self):
        return f"{self.user.username} - {self.exam.title} - {self.score}"

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta

class ExamAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    exam = models.ForeignKey('Exam', on_delete=models.CASCADE)  
    total_time_taken = models.IntegerField(help_text="Total time spent on the exam in seconds")
    start_time = models.DateTimeField(default=now, help_text="Time when the user started the exam")
    end_time = models.DateTimeField(null=True, blank=True, help_text="Time when the user submitted the exam")

    def save(self, *args, **kwargs):
        if self.total_time_taken and not self.end_time:
            self.end_time = self.start_time + timedelta(seconds=self.total_time_taken)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.exam.title} - {self.total_time_taken} sec"


