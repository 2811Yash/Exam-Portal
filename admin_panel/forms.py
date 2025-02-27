from django import forms
from .models import Exam, Question


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ["title", "start_time", "duration"]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "duration": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Duration in minutes"}),
        }

    def clean_duration(self):
        duration = self.cleaned_data.get("duration")
        if duration <= 0:
            raise forms.ValidationError("Duration must be a positive number.")
        return duration

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['exam', 'text', 'options', 'correct_answer']
