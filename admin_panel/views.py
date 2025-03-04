from .models import ExamAttempt
from .forms import ExamForm
from groq import Groq
from dotenv import load_dotenv
import os
from .models import Question,Exam,ExamResult,User
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db.models import Sum, IntegerField
from django.db.models.functions import Cast 
from exams.models import Response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import string,random,json
from django.core.mail import send_mail
from django.utils.timezone import localtime
from json.decoder import JSONDecodeError

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def is_admin(user):
    return user.is_superuser  

def admin_dashboard(request):
    exam=Exam.objects.all()
    if not request.user.is_staff:
        return redirect("admin_login")  # Redirect non-staff users to login page
    return render(request, "admin_dashboard.html", {"user": request.user,"exams":exam})

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

def generate_random_password(length=8):
    """Generate a random password with letters and digits."""
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))



from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def add_student(request):
    if request.method == "POST":
        
        # ✅ Handle adding students
        if request.FILES.get("email_file"):
            email_file = request.FILES["email_file"]
            emails = []

            try:
                for line in email_file:
                    email = line.strip().decode("utf-8")  # Decode bytes to string
                    if email:
                        emails.append(email)
            except Exception as e:
                messages.error(request, "Error reading file: " + str(e))
                return redirect("add_student")

            new_students = []
            for email in emails:
                password = generate_random_password()
                if not User.objects.filter(username=email).exists():
                    user = User.objects.create_user(username=email, email=email, password=password)
                    new_students.append((email, password))

            if not new_students:
                messages.warning(request, "No new students added. Users might already exist.")
                return redirect("add_student")

            email_sender(new_students)
            messages.success(request, f"{len(new_students)} students added successfully!")
            return redirect("add_student")

        # ✅ Handle adding a single student
        email = request.POST.get("username")
        password = generate_random_password()

        if email and not User.objects.filter(username=email).exists():
            user = User.objects.create_user(username=email, email=email, password=password)
            email_sender([(email, password)])
            messages.success(request, "Student added successfully!")
        else:
            messages.warning(request, "User already exists or invalid email.")

        return redirect("add_student")

    # ✅ Fetch students (only regular users, not staff/admins)
    students = User.objects.filter(is_staff=False)
    
    return render(request, "add_student.html", {"students": students})

def student_list(request):
    if request.method == "POST":
        student_ids = request.POST.get("delete_students")
        if student_ids:
            student_ids = student_ids.split(",")  # Convert CSV to list
            User.objects.filter(id__in=student_ids).delete()
            messages.success(request, f"{len(student_ids)} student(s) deleted successfully!")

    students = User.objects.filter(is_staff=False)
    
    return render(request, "student_list.html", {"students": students})

def email_sender(new_students):
    for email, password in new_students:
                try:
                    send_mail(
                        "Your Student Login Credentials",
                        f"Hello,\n\nYour account has been created.\nLogin ID: {email}\nPassword: {password}\n\n",
                        "yash@gmail.com",  # Change this to your admin email
                        [email],
                        fail_silently=False,
                    )
                    print(f"📩 Email sent to {email}")
                except Exception as e:
                    print(f"❌ Error sending email to {email}: {e}")

def exam_list(request):  # Update with the actual view where this needs to be included
    exams = Exam.objects.all().order_by('-start_time')  
    return render(request, 'add_exam.html', {'exams': exams})

def results(request):
    # Calculate user scores
    user_scores = Response.objects.values('user_id', 'exam_id').annotate(
        score=Sum(Cast('is_correct', IntegerField()))
    )

    # Convert start_time to local timezone for attempts
    exam_attempts = ExamAttempt.objects.all()
    for attempt in exam_attempts:
        attempt.start_time = localtime(attempt.start_time)  

    # Update or create exam results
    for entry in user_scores:
        user_id = entry['user_id']
        exam_id = entry['exam_id']
        score = entry['score'] or 0  

        user = User.objects.filter(id=user_id).first()
        exam = Exam.objects.filter(id=exam_id).first()

        if user and exam:
            ExamResult.objects.update_or_create(
                user=user,
                exam=exam,
                defaults={'score': score}
            )

    # Fetch all exams
    exams = Exam.objects.all()

    # Fetch results grouped by exam
    results = ExamResult.objects.select_related('exam', 'user')

    return render(request, 'results.html', {
        'exams': exams,    # Send exams list
        'results': results, # Send exam results
        'attempts': exam_attempts  # Send exam attempts data
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
 # Import forms

def add_exam(request):
    exams = Exam.objects.all()
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
    
    return render(request, "add_exam.html", {"form": form, "exams": exams})

def generate_question_with_ai(topic):
    """Generate a multiple-choice question using AI in JSON format based on a topic."""
    
    prompt = f"""
    Generate a multiple-choice question about {topic} with exactly 4 options and a correct answer. 
    Provide the response strictly in the following JSON format I tshould be the json format strictly:

    {{
        "question": "<question_text>",
        "options": {{
            "a": "<option_1>",
            "b": "<option_2>",
            "c": "<option_3>",
            "d": "<option_4>"
        }},
        "answer": "<correct_answer>"  # Should be the value of that options not a or b or c or d only
    }}
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gemma2-9b-it",
        )

        ai_text = chat_completion.choices[0].message.content.strip()
        
        # Try to parse JSON response
        ai_data = json.loads(ai_text)
        print(ai_data)
        # Validate required keys
        if not all(key in ai_data for key in ["question", "options", "answer"]):
            raise ValueError("AI response is missing required fields!")

        return ai_data["question"], ai_data["options"], ai_data["answer"]

    except JSONDecodeError:
        raise ValueError("AI response is not valid JSON!")
    
    except Exception as e:
        raise ValueError(f"An error occurred while processing AI response: {str(e)}")

def add_question(request, exam_id):
    """Handles adding a new question to a specific exam."""
    
    # Get the exam by ID or return 404 if not found
    exam = get_object_or_404(Exam, id=exam_id)
    ai_generated_question = request.session.get("ai_question", None)  # Retrieve AI-generated question from session

    if request.method == "POST":
        text = request.POST.get("text")
        options = request.POST.get("options").split(",")  
        correct_answer = request.POST.get("correct_answer")

        if text and options and correct_answer:
            options_dict = {
                letter: option.strip() for letter, option in zip(string.ascii_lowercase, options) if option.strip()
            }
            print(options_dict)

            Question.objects.create(
                exam=exam,  # Associate question with the selected exam
                text=text.strip(),
                options=options_dict,
                correct_answer=correct_answer.strip(),
            )

            request.session.pop("ai_question", None)  # Clear session after saving
            messages.success(request, "Question added successfully!")
            return redirect("add_question", exam_id=exam.id)  # Redirect to the same exam's add question page

    # Handle AI question generation
    if "generate_ai" in request.GET:
        topic = request.GET.get("topic", "General Knowledge")
        
        try:
            question_text, options, correct_answer = generate_question_with_ai(topic)
            print("yash")
            print(question_text)
            ai_generated_question = {
                "text": question_text,
                "options": options,
                "correct_answer": correct_answer
            }
            request.session["ai_question"] = ai_generated_question

        except ValueError as e:
            messages.error(request, str(e))

    return render(
        request, 
        "add_question.html", 
        {"ai_generated_question": ai_generated_question, "exam": exam}
    )

def question_list(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = Question.objects.filter(exam=exam)  # Fetch all questions for the selected exam
    return render(request, "question_list.html", {"exam": exam, "questions": questions})

def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    exam_id = question.exam.id  # Store exam_id to redirect back after deletion
    question.delete()
    messages.success(request, "Question deleted successfully!")
    return redirect("question_list", exam_id=exam_id)  # Redirect to the list of questions


def exam_results(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    results = ExamResult.objects.filter(exam=exam)
    attempts = ExamAttempt.objects.filter(exam=exam)

    return render(request, "result_page.html", {
        "exam": exam,
        "results": results,
        "attempts": attempts,
    })
