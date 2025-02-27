from .models import ExamAttempt
from .forms import ExamForm
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
import os
from .models import Question,Exam,ExamResult,User
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db.models import Sum, IntegerField
from django.db.models.functions import Cast 
from exams.models import Response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages


client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def is_admin(user):
    return user.is_superuser  

def generate_question_with_ai(topic):
    """Generate a multiple-choice question using AI based on a topic."""
    
    prompt = f"""
    Generate a multiple-choice question about {topic} with exactly 4 options and a correct answer.
    Format the response like this:

    Question: <question_text>
    a) <option_1>
    b) <option_2>
    c) <option_3>
    d) <option_4>
    Answer: <correct_answer_option>
    """

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gemma2-9b-it",
    )

    ai_text = chat_completion.choices[0].message.content.strip()
    print(ai_text) 

    
    lines = ai_text.split("\n")
    
    if len(lines) < 6:  
        raise ValueError("AI response format is incorrect!")

    question_text = lines[0].replace("Question: ", "").strip()
    options = [lines[1].split(") ")[1], lines[2].split(") ")[1], lines[3].split(") ")[1], lines[4].split(") ")[1]]
    correct_answer = lines[5].replace("Answer: ", "").strip()

    return question_text, options, correct_answer

def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect("admin_login")  # Redirect non-staff users to login page
    return render(request, "admin_dashboard.html", {"user": request.user})



def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        print(username)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_staff:  # Check if the user is a staff member
                login(request, user)
                return redirect("admin_dashboard")  # Redirect to admin dashboard
            else:
                return render(request, "admin_login.html", {"error": "You are not authorized as staff."})
        else:
            return render(request, "admin_login.html", {"error": "Invalid credentials. Try again."})

    return render(request, "admin_login.html")

def admin_logout(request):
    logout(request)
    return redirect("admin_login")

def staff_signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(request, "staff_signup.html", {"error": "Passwords do not match!"})

        if User.objects.filter(username=username).exists():
            return render(request, "staff_signup.html", {"error": "Username already taken!"})

        user = User.objects.create_user(username=username, password=password)
        user.is_staff = True  # Assign staff status
        user.save()

        login(request, user)  # Automatically log in the user
        return redirect("admin_dashboard")  # Redirect to the admin dashboard

    return render(request, "staff_signup.html")



def exam_list(request):  # Update with the actual view where this needs to be included
    exams = Exam.objects.all().order_by('-start_time')  
    return render(request, 'add_exam.html', {'exams': exams})


from django.utils.timezone import localtime

def results(request):
    user_scores = Response.objects.values('user_id', 'exam_id').annotate(
        score=Sum(Cast('is_correct', IntegerField()))
    )
    
    exam_attempts = ExamAttempt.objects.all()
    
    # Convert start_time to local timezone
    for attempt in exam_attempts:
        attempt.start_time = localtime(attempt.start_time)  # Converts to local time

    for entry in user_scores:
        exam_id = entry['exam_id']
        user_id = entry['user_id']
        score = entry['score'] or 0  
        user = User.objects.filter(id=user_id).first()
        exam = Exam.objects.filter(id=exam_id).first()

        ExamResult.objects.update_or_create(
            user=user,
            score=score, 
            exam=exam
        )

    results = ExamResult.objects.all()
    users = User.objects.all()  

    return render(request, 'results.html', {
        'results': results,
        'users': users,
        'attempts': exam_attempts
    })




def delete_exam(request):
    exams = Exam.objects.all()  # Fetch all exams

    if request.method == "POST":
        exam_id = request.POST.get("exam_id")  # Get selected exam ID
        if exam_id:
            exam = get_object_or_404(Exam, id=exam_id)
            exam.delete()
            messages.success(request, f"Exam '{exam.title}' deleted successfully!")
            return redirect("delete_exam")  # Refresh page after deletion

    return render(request, "delete_exam.html", {"exams": exams})

def add_exam(request):
    exams=Exam.objects.all()
    if request.method == "POST":
        form = ExamForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam added successfully!")
            return redirect("exam_list")  # Redirect to list of exams
        else:
            messages.error(request, "There was an error. Please check the form.")
    else:
        form = ExamForm()
    
    return render(request, "add_exam.html", {"form": form,"exams":exams})


import json
import string


def add_question(request):
    ai_generated_question = request.session.get("ai_question", None)  # Retrieve AI-generated question from session
    exams=Exam.objects.all()
    if request.method == "POST":
        text = request.POST.get("text")
        options = request.POST.get("options").split("\n")  
        correct_answer = request.POST.get("correct_answer")
        exam_id = request.POST.get("exam_id")  
        # print(exam)

        if text and options and correct_answer and exam_id:
            options_dict = {
            letter: option.strip() for letter, option in zip(string.ascii_lowercase, options) if option.strip()}
            print(options_dict)
            Question.objects.create(
                exam_id=exam_id,  # Associate question with the selected exam
                text=text.strip(),
                options=options_dict,
                correct_answer=correct_answer.strip(),
            )
            request.session.pop("ai_question", None)  # Clear session after saving
            return redirect("add_question")  # Redirect to refresh the page

    # Handle AI question generation
    if "generate_ai" in request.GET:
        topic = request.GET.get("topic", "General Knowledge")
        question_text, options, correct_answer = generate_question_with_ai(topic)

        ai_generated_question = {
            "text": question_text,
            "options": options,
            "correct_answer": correct_answer
        }

        # Store AI-generated question in session
        request.session["ai_question"] = ai_generated_question

    return render(request, "add_question.html", {"ai_generated_question": ai_generated_question,"exams":exams})




# <form method="get">
#                 <div class="mb-3">
#                     <label class="form-label">Select Exam</label>
#                     <select class="form-control" name="exam_id" required>
#                         <option value="">-- Choose an Exam --</option>
#                         {% for exam in exams %}
#                             <option value="{{ exam.id }}">{{ exam.title }}</option>
#                         {% endfor %}
#                     </select>
#                 </div>