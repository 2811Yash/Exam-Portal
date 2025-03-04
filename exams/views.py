from django.utils import timezone
from django.http import JsonResponse
from admin_panel.models import ExamAttempt
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from datetime import timedelta
from .models import Exam, Question, Response
import json

@login_required
def dashboard(request):
    current_time = timezone.now()  # Get current time
    next_24_hours = current_time + timedelta(hours=24)  # Get time 24 hours from now

    # Fetch exams that have already started OR will start within the next 24 hours
    available_exams = Exam.objects.filter(start_time__lte=next_24_hours)

    return render(request, 'dashboard.html', {
        'exams': available_exams,
        'current_time': current_time,  # Send current time to the template
    })


def take_exam(request, exam_id):
    exam = Exam.objects.get(id=exam_id)
    questions = Question.objects.filter(exam=exam)

    # Convert questions and options into a JSON-friendly format
    questions_list = [
        {"id": q.id, "text": q.text, "options": list(q.options.values())}
        for q in questions
    ]
    # print(questions_list)

    return render(request, "take_exam.html", {
        "exam": exam,
        "questions_json": json.dumps(questions_list)
    })

def submit_exam(request, exam_id):
    if request.method == "POST":
        exam = get_object_or_404(Exam, id=exam_id)

        # Prevent multiple submissions
        if ExamAttempt.objects.filter(user=request.user, exam=exam).exists():
            messages.error(request, "You have already submitted this exam!")
            return redirect("exam_submission_confirmation")  

        start_time = now()  # Capture submission time
        total_time_taken = int(request.POST.get("total_time", 0))  # Fetch time from frontend

        for question_id, answer in request.POST.items():
            if question_id.startswith("q_"):
                q = Question.objects.get(id=int(question_id[2:]))
                is_correct = q.correct_answer == answer

                Response.objects.create(user=request.user, exam=exam, question=q, selected_answer=answer, is_correct=is_correct)

        # Save exam time in ExamAttempt model
        ExamAttempt.objects.create(
            user=request.user,
            exam=exam,
            total_time_taken=total_time_taken,
            start_time=start_time,
            end_time=start_time + timedelta(seconds=total_time_taken)
        )

        messages.success(request, "Exam submitted successfully! You have been logged out.")

        logout(request)

        return redirect("exam_submission_confirmation")  

    return JsonResponse({"error": "Invalid request!"}, status=400)


def exam_results(request):
    results = Response.objects.filter(user=request.user)
    return render(request, 'results.html', {'results': results})



def login_view(request):
    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        print("enter")
        if user is not None:
            print("login")
            login(request, user)
            return redirect('dashboard')  
        else:
            return render(request, "login.html", {"error": "Invalid credentials. Try again."})

    return render(request, 'login.html')



def logout_view(request):
    logout(request)
    return redirect('login')

def exam_submission_confirmation(request):
    return render(request, "submit.html")
