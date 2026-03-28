
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from main.models import Student, Subject, Question, TestResult, FinalResultHistory
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from django.db.models import Value, F, BooleanField, CharField


from django.db.models import Q

def admin_login(request):
    if request.user.is_authenticated:
        return redirect('adminpanel_dashboard')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser or user.is_staff:
                login(request, user)
                return redirect('adminpanel_dashboard')  # ✅ must match your urls.py name
            else:
                messages.error(request, "You are not authorized to access the admin panel.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "adminpanel/admin_login.html")

def admin_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('adminpanel_login')


from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    """Allow only admin/staff users to access the view."""
    decorated_view_func = user_passes_test(
        lambda u: u.is_authenticated and (u.is_staff or u.is_superuser),
        login_url='adminpanel_login'  # name of your admin login URL
    )(view_func)
    return decorated_view_func


@admin_required
def dashboard(request):
    context = {
        "student_count": Student.objects.count(),
        "subject_count": Subject.objects.count(),
        "question_count": Question.objects.count(),
        "result_count": TestResult.objects.count(),
        "recent_results": TestResult.objects.select_related('student', 'subject').order_by('-date_taken')[:5]
    }
    return render(request, "adminpanel/admin_dashboard.html", context)



@admin_required
def student_list(request):
    query = request.GET.get('q', '')
    students = Student.objects.all().order_by('-id')

    if query:
        students = students.filter(
            Q(firstname__icontains=query) |
            Q(lastname__icontains=query) |
            Q(user_id__icontains=query)
        )

    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'adminpanel/students.html', {'page_obj': page_obj})

import random
from django.contrib import messages
from django.shortcuts import render, redirect
from main.models import Student

@admin_required
def add_student(request):
    if request.method == "POST":
        firstname = request.POST.get("firstname", "").strip()
        middlename = request.POST.get("middlename", "").strip()
        lastname = request.POST.get("lastname", "").strip()
        password = request.POST.get("password", "").strip()

        if firstname and lastname and password:
            base_user_id = (firstname + lastname).lower()
            user_id = base_user_id

            # 🔁 If username exists → add @ + 3 digits
            if Student.objects.filter(user_id=user_id).exists():
                while True:
                    suffix = random.randint(100, 999)
                    user_id = f"{base_user_id}@{suffix}"
                    if not Student.objects.filter(user_id=user_id).exists():
                        break

                messages.warning(
                    request,
                    f"Username already existed. New User ID generated: {user_id}"
                )

            Student.objects.create(
                firstname=firstname,
                lastname=lastname,
                middlename=middlename,
                user_id=user_id,
                password=password,  # ⚠️ plain text (see note below)
            )

            messages.success(request, "Student added successfully!")
            return redirect("adminpanel_students")

        messages.error(request, "All fields are required.")

    return render(request, "adminpanel/add_student.html")




@admin_required
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    messages.success(request, "Student deleted successfully!")
    return redirect("custom_admin_students")



@admin_required
def subject_list(request):
    subjects = Subject.objects.all().order_by('id')
    paginator = Paginator(subjects, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'adminpanel/subjects.html', {'page_obj': page_obj})


@admin_required
def question_list(request):
    questions = Question.objects.select_related('subject').all()
    query = request.GET.get('q')
    if query:
        # Search by question text OR subject name
        questions = Question.objects.filter(
            Q(question_text__icontains=query) | Q(subject__name__icontains=query)
        )
    else:
        questions = Question.objects.all()
    return render(request, "adminpanel/questions.html", {"questions": questions})

@admin_required
def mock_result_list(request):
    query = request.GET.get("search", "")
    start = request.GET.get("start_date")
    end = request.GET.get("end_date")

    results = TestResult.objects.select_related("student", "subject")

    # --- Apply Search ---
    if query:
        results = results.filter(
            Q(student__name__icontains=query) |
            Q(subject__name__icontains=query)
        )

    # --- Filter by Date ---
    if start:
        results = results.filter(date_taken__gte=start)

    if end:
        results = results.filter(date_taken__lte=end)

    results = results.order_by("-date_taken")

    paginator = Paginator(results, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "adminpanel/results.html", {
        "page_obj": page_obj,
        "search": query,
        "start_date": start,
        "end_date": end,
    })




@admin_required
def student_result_history(request, username):
    student = get_object_or_404(Student, user_id=username)

    # Filter type
    result_type = request.GET.get("type", "all")

    # -------- MOCK RESULTS --------
    mock_qs = TestResult.objects.filter(student=student).select_related("subject")

    mock_results = [
        {
            "subject": r.subject.name,
            "score": r.score,
            "total": r.total_questions,
            "percentage": r.percentage,
            "remark": r.remark,
            "date": r.date_taken,
            "type": "mock",
        }
        for r in mock_qs
    ]

    # -------- FINAL RESULTS --------
    final_qs = FinalResultHistory.objects.filter(student=student)

    final_results = [
        {
            "subject": "Final Test",         # Replace subject name → Final Test
            "score": None,
            "total": None,
            "percentage": r.average_percentage,
            "remark": r.remark,
            "date": r.test_date,
            "type": "final",
        }
        for r in final_qs
    ]

    # -------- COMBINE BASED ON FILTER --------
    if result_type == "mock":
        combined = mock_results
    elif result_type == "final":
        combined = final_results
    else:
        combined = mock_results + final_results   # BOTH

    # Sort by date DESC
    combined.sort(key=lambda x: x["date"], reverse=True)

    # Pagination
    paginator = Paginator(combined, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "adminpanel/student_result_history.html", {
        "student": student,
        "page_obj": page_obj,
        "result_type": result_type,
    })



@admin_required 
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == 'POST':
        student.firstname = request.POST.get('firstname')
        student.middlename = request.POST.get('middlename')
        student.lastname = request.POST.get('lastname')
        student.user_id = request.POST.get('user_id')
        student.password = request.POST.get('password')
        student.save()
        return redirect('adminpanel_students')

    return render(request, 'adminpanel/edit_student.html', {'student': student})


@admin_required
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    return redirect('adminpanel_students')




import os
import csv
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.apps import apps
 # adjust app name if different


@admin_required
def upload_fixture(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("fixture_file")

        if not uploaded_file:
            messages.error(request, "⚠️ No file selected.")
            return redirect("upload_fixture")

        if not uploaded_file.name.lower().endswith(".csv"):
            messages.error(request, "❌ Only CSV files are allowed.")
            return redirect("upload_fixture")

        # ✅ Subject name from file name
        subject_name = os.path.splitext(uploaded_file.name)[0].strip()
        if not subject_name:
            messages.error(request, "❌ Invalid file name. It must match a subject name.")
            return redirect("upload_fixture")

        # ✅ Locate fixtures folder inside the 'main' app
        app_config = apps.get_app_config('main')
        fixtures_dir = os.path.join(app_config.path, "fixtures")
        os.makedirs(fixtures_dir, exist_ok=True)

        file_path = os.path.join(fixtures_dir, f"{subject_name}.csv")

        # ✅ Save uploaded CSV
        with open(file_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        added_count = 0
        skipped_count = 0

        try:
            with open(file_path, mode="r", encoding="utf-8") as csv_file:
                reader = csv.DictReader(csv_file)

                with transaction.atomic():
                    subject, _ = Subject.objects.get_or_create(name=subject_name)

                    for row in reader:
                        question_text = row.get("question_text", "").strip()
                        if not question_text:
                            continue

                        # ✅ Skip exact duplicate question (case-insensitive)
                        if Question.objects.filter(question_text__iexact=question_text).exists():
                            skipped_count += 1
                            continue

                        Question.objects.create(
                            question_text=question_text,
                            option1=row.get("option1", "").strip(),
                            option2=row.get("option2", "").strip(),
                            option3=row.get("option3", "").strip(),
                            option4=row.get("option4", "").strip(),
                            correct_option=row.get("correct_option", "").strip(),
                            subject=subject,
                        )
                        added_count += 1

            messages.success(
                request,
                f"✅ Added {added_count} new question(s) for '{subject_name}'. Skipped {skipped_count} duplicate(s)."
            )

        except Exception as e:
            messages.error(request, f"❌ Error while uploading '{subject_name}': {str(e)} (rolled back)")

        finally:
            # ✅ Always delete uploaded file after processing
            if os.path.exists(file_path):
                os.remove(file_path)

        return redirect("upload_fixture")

    return render(request, "adminpanel/upload_fixture.html")


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

@admin_required
def edit_question(request, id):
    question = get_object_or_404(Question, id=id)
    subjects = Subject.objects.all()  # to populate the dropdown

    if request.method == "POST":
        # Get data from POST
        question_text = request.POST.get("question_text")
        subject_id = request.POST.get("subject")
        option1 = request.POST.get("option1")
        option2 = request.POST.get("option2")
        option3 = request.POST.get("option3")
        option4 = request.POST.get("option4")
        correct_answer = request.POST.get("correct_answer")
        marks = request.POST.get("marks")

        # Update question object
        question.question_text = question_text
        question.subject_id = subject_id
        question.option1 = option1
        question.option2 = option2
        question.option3 = option3
        question.option4 = option4
        question.correct_answer = correct_answer
        question.save()

        messages.success(request, "Question updated successfully!")
        return redirect('question_list')

    return render(request, "adminpanel/edit_question.html", {"question": question, "subjects": subjects})


@admin_required
def delete_question(request, id):
    question = get_object_or_404(Question, id=id)
    question.delete()
    messages.success(request, "Question deleted successfully!")
    return redirect('question_list')

# --------------------------------------------------------------

from django.shortcuts import render
from django.db.models import Q
from main.models import FinalQuestion  # import your model properly

@admin_required
def final_question_list(request):
    query = request.GET.get('q')
    if query:
        final_questions = FinalQuestion.objects.filter(
            Q(question_text__icontains=query) | Q(subject__name__icontains=query)
        ).select_related('subject')
    else:
        final_questions = FinalQuestion.objects.select_related('subject').all()

    return render(request, "adminpanel/final_questions.html", {"final_questions": final_questions})


import os
import csv
import chardet
from django.apps import apps
from django.db import transaction
from django.contrib import messages
from django.shortcuts import render, redirect
from main.models import FinalQuestion, Subject


@admin_required
def upload_final_fixture(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("fixture_file")

        if not uploaded_file:
            messages.error(request, "⚠️ No file selected.")
            return redirect("upload_final_fixture")

        if not uploaded_file.name.lower().endswith(".csv"):
            messages.error(request, "❌ Only CSV files are allowed.")
            return redirect("upload_final_fixture")

        # ✅ Subject name from file name (e.g. "Math.csv" → "Math")
        subject_name = os.path.splitext(uploaded_file.name)[0].strip()
        if not subject_name:
            messages.error(request, "❌ Invalid file name. It must match a subject name.")
            return redirect("upload_final_fixture")

        # ✅ Create or confirm folder in adminpanel/fixtures_final/
        app_config = apps.get_app_config('adminpanel')
        fixtures_dir = os.path.join(app_config.path, "fixtures_final")
        os.makedirs(fixtures_dir, exist_ok=True)

        file_path = os.path.join(fixtures_dir, f"{subject_name}.csv")

        # ✅ Save uploaded file
        with open(file_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        added_count = 0
        skipped_count = 0

        try:
            # ✅ Detect file encoding
            with open(file_path, 'rb') as raw_file:
                result = chardet.detect(raw_file.read())
                detected_encoding = result.get('encoding') or 'utf-8'

            # ✅ Read CSV with detected encoding
            with open(file_path, mode="r", encoding=detected_encoding, errors="replace") as csv_file:
                reader = csv.DictReader(csv_file)

                with transaction.atomic():
                    subject, _ = Subject.objects.get_or_create(name=subject_name)

                    for row in reader:
                        question_text = row.get("question_text", "").strip()
                        if not question_text:
                            continue

                        # ✅ Check duplicates ONLY in the same subject
                        if FinalQuestion.objects.filter(
                            subject=subject,
                            question_text__iexact=question_text
                        ).exists():
                            skipped_count += 1
                            continue

                        FinalQuestion.objects.create(
                            question_text=question_text,
                            option1=row.get("option1", "").strip(),
                            option2=row.get("option2", "").strip(),
                            option3=row.get("option3", "").strip(),
                            option4=row.get("option4", "").strip(),
                            correct_answer=row.get("correct_answer", "").strip(),
                            subject=subject,
                        )
                        added_count += 1

            messages.success(
                request,
                f"✅ Added {added_count} new final question(s) for '{subject_name}'. Skipped {skipped_count} duplicate(s)."
            )

        except Exception as e:
            messages.error(
                request,
                f"❌ Error while uploading final fixture for '{subject_name}': {str(e)} (rolled back)"
            )

        finally:
            # ✅ Clean up uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)

        return redirect("upload_final_fixture")

    return render(request, "adminpanel/upload_final_fixture.html")



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from main.models import FinalQuestion, Subject


@admin_required
def edit_final_question(request, id):
    """Edit a Final Question"""
    question = get_object_or_404(FinalQuestion, id=id)
    subjects = Subject.objects.all()

    if request.method == "POST":
        question.question_text = request.POST.get("question_text", "").strip()
        question.option1 = request.POST.get("option1", "").strip()
        question.option2 = request.POST.get("option2", "").strip()
        question.option3 = request.POST.get("option3", "").strip()
        question.option4 = request.POST.get("option4", "").strip()
        question.correct_answer = request.POST.get("correct_answer", "").strip()

        subject_id = request.POST.get("subject")
        if subject_id:
            question.subject = get_object_or_404(Subject, id=subject_id)

        question.save()
        messages.success(request, "✅ Final question updated successfully.")
        return redirect("final_question_list")

    return render(request, "adminpanel/edit_final_question.html", {
        "question": question,
        "subjects": subjects
    })


@admin_required
def delete_final_question(request, id):
    question = get_object_or_404(FinalQuestion, id=id)
    question.delete()
    messages.success(request, "✅ Final question deleted successfully!")
    return redirect('final_question_list')




@admin_required
def final_result_list(request):
    query = request.GET.get("search", "")
    start = request.GET.get("start_date")
    end = request.GET.get("end_date")

    results = FinalResultHistory.objects.select_related("student")

    # --- Apply search ---
    if query:
        results = results.filter(
            Q(student__name__icontains=query)
        )

    # --- Apply date filter ---
    if start:
        results = results.filter(test_date__gte=start)

    if end:
        results = results.filter(test_date__lte=end)

    results = results.order_by("-test_date")

    paginator = Paginator(results, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "adminpanel/final_results.html", {
        "page_obj": page_obj,
        "search": query,
        "start_date": start,
        "end_date": end,
    })


from collections import defaultdict

@admin_required
def final_result_history(request, result_id):
    result = get_object_or_404(FinalResultHistory, id=result_id)

    # ---------- CALCULATE SUBJECT-WISE PERCENTAGE FROM review_data ----------
    subject_map = defaultdict(lambda: {"correct": 0, "total": 0})

    for item in result.review_data:
        subject = item["subject"]
        subject_map[subject]["total"] += 1
        if item.get("is_correct"):
            subject_map[subject]["correct"] += 1

    subject_data = {}
    for subject, data in subject_map.items():
        pct = round((data["correct"] / data["total"]) * 100, 2)
        subject_data[subject] = {
            "percentage": pct,
            "remark": "PASS" if pct >= 70 else "FAIL"
        }

    # average
    avg = sum(v["percentage"] for v in subject_data.values()) / len(subject_data) if subject_data else 0
    result.average_percentage = round(avg, 2)

    return render(request, "adminpanel/final_result_history.html", {
        "result": result,
        "subject_data": subject_data,  # 👈 send processed data to template
    })


def admin_final_review(request, result_id):
    result = get_object_or_404(FinalResultHistory, id=result_id)

    return render(request, "adminpanel/final_review.html", {
        "student": result.student,
        "review_data": result.review_data,
        "average_percentage": result.average_percentage,
        "subject_percentages": result.subject_percentages,
        "remark": result.remark,
        "date": result.test_date,
    })
