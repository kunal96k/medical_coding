from .models import  Student, Subject, TestResult,Question
from django.shortcuts import get_object_or_404,render, redirect
from django.contrib import messages
from datetime import date
from .decorators import student_login_required


def student_login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        # 1️⃣ Empty fields check
        if not username or not password:
            messages.error(request, "⚠️ Username and password are required.")
            return redirect("login")

        # 2️⃣ Username check
        try:
            student = Student.objects.get(user_id=username)
        except Student.DoesNotExist:
            messages.error(request, "❌ Invalid username or password.")
            return redirect("login")

        # 3️⃣ Password check
        if student.password != password:
            messages.error(request, "❌ Invalid username or password.")
            return redirect("login")  # ✅ FIXED

        # 4️⃣ Login success
        request.session["student_id"] = student.id

        # 🔐 First login → force password change
        if not student.has_changed_password:
            return redirect("change_password")

        messages.success(request, f"✅ Welcome {student.firstname}!")
        return redirect("student_dashboard")

    return render(request, "login.html")




def student_logout(request):
    request.session.flush()  # Clear all session data
    return redirect("login")


def change_password(request):
    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("student_login")

    student = Student.objects.get(id=student_id)

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "❌ Passwords do not match.")
            return redirect("change_password")

        student.password = new_password
        student.has_changed_password = True
        student.save()

        messages.success(request, "✅ Password updated successfully.")
        return redirect("login")

    return render(request, "change_password.html")

@student_login_required
def student_dashboard(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect("login")

    student = get_object_or_404(Student, id=request.session['student_id'])  # use 'id', not 'student_id'

    subjects = Subject.objects.all()
    selected_subject_id = request.GET.get('subject')
    selected_subject = None
    chart_data = []

    if selected_subject_id:
        student = get_object_or_404(Student, id=request.session['student_id'])
    elif subjects:
        selected_subject = subjects.first()

    if selected_subject:
        results = TestResult.objects.filter(student=student, subject=selected_subject).order_by('date_taken')
        chart_data = [
            {"date": r.date_taken.strftime("%d-%m-%Y"), "score": r.score, "total": r.total_questions}
            for r in results
        ]

    context = {
        "student": student,
        "subjects": subjects,
        "selected_subject": selected_subject,
        "chart_data": chart_data,
        "active_page": "student_dashboard",
    }
    return render(request, "progress.html", context)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from .models import Student, TestResult, Subject
import json
from datetime import datetime


@student_login_required
def student_progress(request):
    if "student_id" not in request.session:
        return redirect("login")

    student = get_object_or_404(Student, id=request.session["student_id"])
    subjects = Subject.objects.all()

    selected_subject_id = request.GET.get("subject")
    selected_subject = None
    chart_data = []

    if selected_subject_id:
        selected_subject = get_object_or_404(Subject, id=selected_subject_id)

        results = TestResult.objects.filter(
            student=student,
            subject=selected_subject
        ).order_by("date_taken")

        for r in results:
            percentage = round((r.score / 30) * 100, 2)
            chart_data.append({
                "date": r.date_taken.strftime("%d-%m-%Y"),
                "score": r.score,
                "percentage": percentage,
            })

    context = {
        "student": student,
        "subjects": subjects,
        "selected_subject": selected_subject,
        "chart_data": chart_data,
    }

    return render(request, "progress.html", context)


@student_login_required
def start_test(request):

    allowed = ["Anatomy and Med Term and Compliance and Coding Guidelines CPC","10K 20K 30K Series","40K 50K 60K Series","70K 80K 90K Series","99K and 00 Series","HCPCS","ICD PART A","ICD PART B","ICD PART C","Cases"]
    subjects = Subject.objects.filter(name__in=allowed)

    if request.method == "POST":
        selected_subject_id = request.POST.get("subject")
        if selected_subject_id:
            subject = Subject.objects.get(id=selected_subject_id)

            for key in ["exam_start_time", "selected_questions", "score", "total_questions", "answers_review", "selected_subject"]:
                request.session.pop(key, None)

            return redirect(f'/test/?subject={subject.name}')

    return render(request, 'start_test.html', {
        'subjects': subjects,
        "active_page": "start_test"
    })




from django.utils import timezone

@student_login_required
def mcq_test(request):
    if 'student_id' not in request.session:
        return redirect('login')

    student = get_object_or_404(Student, id=request.session['student_id'])
    subjects = Subject.objects.all()
    selected_subject = request.GET.get('subject')

    exam_duration = 60 * 60  # 1 hour in seconds

    # --------------------d
    # Timer setup
    # --------------------
    if 'exam_start_time' not in request.session:
        request.session['exam_start_time'] = timezone.now().isoformat()

    start_time = timezone.datetime.fromisoformat(request.session['exam_start_time'])
    elapsed = (timezone.now() - start_time).total_seconds()
    remaining_time = exam_duration - int(elapsed)
    if remaining_time <= 0 and request.method != 'POST':
        return redirect("result")


    # --------------------
    # Handle submission
    # --------------------
    if request.method == 'POST':
        score = 0
        total = 0
        answers_review = []
        selected_subject_obj = None

        for key, value in request.POST.items():
            if key.startswith("question_"):
                qid = int(key.split("_")[1])
                try:
                    question = Question.objects.get(id=qid)
                    selected_subject_obj = question.subject
                    total += 1
                    correct = (value.strip() == question.correct_answer.strip())
                    if correct:
                        score += 1

                    answers_review.append({
                        "question": question.question_text,
                        "selected": value,
                        "correct": question.correct_answer,
                        "is_correct": correct,
                    })

                except Question.DoesNotExist:
                    continue

        if selected_subject_obj:
            TestResult.objects.create(
                student=student,
                subject=selected_subject_obj,
                score=score,
                total_questions=total,
                attempt_no=TestResult.objects.filter(student=student, subject=selected_subject_obj).count() + 1
            )

        # Store results in session for result page
        request.session['score'] = score
        request.session['total_questions'] = total
        request.session['answers_review'] = answers_review
        request.session['selected_subject'] = selected_subject

        # ✅ Clear exam session data after completion
        request.session.pop('exam_start_time', None)
        request.session.pop('selected_questions', None)
        request.session.modified = True

        return redirect("result")

    # --------------------
    # Question selection
    # --------------------
    questions = []
    if selected_subject:
        if 'selected_questions' not in request.session:
            selected_qs = list(
                Question.objects.filter(subject__name=selected_subject)
                .order_by("?")[:30]
            )
            selected_ids = [q.id for q in selected_qs]
            request.session['selected_questions'] = selected_ids
            request.session.modified = True
        else:
            selected_ids = request.session['selected_questions']

        # Fetch questions and preserve the order manually
        questions_dict = {q.id: q for q in Question.objects.filter(id__in=selected_ids)}
        questions = [questions_dict[qid] for qid in selected_ids]


    return render(request, 'test.html', {
        'subjects': subjects,
        'questions': questions,
        'selected_subject': selected_subject,
        'remaining_time': remaining_time,
    })

@student_login_required
def submit_test(request):
    
    if request.method == "POST":
        return mcq_test(request)
    return redirect("student_dashboard")


def result(request):
    if 'student_id' not in request.session:
        return redirect('login')

    student = get_object_or_404(Student, id=request.session['student_id'])

    score = int(request.session.get('score', 0))
    total = int(request.session.get('total_questions', 0))
    answers_review = request.session.get('answers_review', [])
    selected_subject = request.session.get('selected_subject', "N/A")
    percentage = (score / total * 100) if total > 0 else 0

    context = {
        'student_id': student.id,
        'firstname': student.firstname,
        'lastname': student.lastname,
        'score': score,
        'total': total,
        'percentage': round(percentage, 2),
        'answers_review': answers_review,
        'test_date': date.today().strftime("%d-%m-%Y"),
        'subject': selected_subject,
        "active_page": "result",
    }

    return render(request, 'result.html', context)

@student_login_required
def test_history(request):
    if 'student_id' not in request.session:
        return redirect('login')

    studentid = request.session['student_id']
    student = get_object_or_404(Student, id=request.session['student_id'])

    results = TestResult.objects.filter(student=student).order_by('-date_taken')

    # If you still want to show last test score:
    last_result = results.first()
    if last_result:
        score = last_result.score
        total = last_result.total_questions
        percentage = (score / total * 100) if total > 0 else 0
    else:
        score, total, percentage = 0, 0, 0

    return render(
        request,
        "test_history.html",
        {
            "student": student,
            "results": results,
            "score": score,
            "total": total,
            "percentage": percentage,
            "active_page": "history",
        }
    )

@student_login_required
def review(request):
    
    answers = request.session.get("answers_review", []) 
    score = request.session.get("score", 0)
    total = request.session.get("total_questions", 0)  
    
   
    return render(request, "review.html", {
        "answers": answers,
        "score": score,
        "total": total,
        
    })


import json, random
from django.shortcuts import render, redirect, get_object_or_404
from .models import Student, Subject, FinalQuestion

@student_login_required
def finaltest(request):
    if 'student_id' not in request.session:
        return redirect('login')

    student = get_object_or_404(Student, id=request.session['student_id'])

    # --- Define subjects and your custom question limits ---
    subject_limits = {
        "00K Series": 4, "10K Series": 6,
        "20K Series": 6, "30K Series": 6,
        "40K Series": 6, "50K Series": 6,
        "60K Series": 6, "70K Series": 6,
        "80K Series": 6, "90K Series": 6,
        "99K Series": 6, "Anatomy": 4,
        "Cases": 10, "Coding Guidelines": 6,
        "Compliance": 4, "HCPCS": 3,
        "ICD": 5, "Medical Terminology": 4,
    }

    # ---------------- SUBJECT TITLES ----------------
    subject_titles = {
        "00K Series": "Anesthesia",
        "10K Series": "Integumentary System",
        "20K Series": "Musculoskeletal System",
        "30K Series": "Respiratory & Cardiovascular System",
        "40K Series": "Digestive System",
        "50K Series": "Genitourinary System (Urinary, Male/Female genital)",
        "60K Series": "Endocrine & Nervous System",
        "70K Series": "Radiology",
        "80K Series": "Pathology & Laboratory",
        "90K Series": "Medicine",
        "99K Series": "Evaluation & Management (E&M Services)",
        "Anatomy": "Human Anatomy Overview",
        "Coding Guidelines": "CPT & ICD Coding Guidelines",
        "Compliance": "Compliance & Regulatory Requirements",
        "Cases": "Real-world Case Studies",
        "HCPCS": "HCPCS Level II Codes",
        "ICD": "ICD-10-CM Diagnosis Coding",
        "Medical Terminology": "Medical Terminology Basics",
    }


    first_subject_name = next(iter(subject_limits.keys()))

    header_title = subject_titles.get(first_subject_name, "")

   
    subjects = Subject.objects.filter(name__in=subject_limits.keys())

   
    session_limits_json = request.session.get('final_subject_limits')
    current_limits_json = json.dumps(subject_limits, sort_keys=True)

    if ('final_selected_questions' not in request.session) or (session_limits_json != current_limits_json):
        selected_data = {}

        for subject in subjects:
            limit = subject_limits.get(subject.name, 5)
            all_questions = list(FinalQuestion.objects.filter(subject=subject))
            random.shuffle(all_questions)
            selected = all_questions[:limit]
            selected_data[subject.name] = [q.id for q in selected]

        request.session['final_selected_questions'] = selected_data
        request.session['final_subject_limits'] = current_limits_json
        request.session.modified = True

    else:
        selected_data = request.session['final_selected_questions']

    # --- Fetch selected questions ---
    all_selected_ids = [qid for ids in selected_data.values() for qid in ids]

    question_list = []
    counter = 1

    for subject_name in subject_limits.keys():
        ids = selected_data.get(subject_name, [])
        subject_questions = FinalQuestion.objects.filter(id__in=ids).select_related('subject')

        id_order = {id_: idx for idx, id_ in enumerate(ids)}
        subject_questions = sorted(subject_questions, key=lambda q: id_order.get(q.id, 0))

        for q in subject_questions:
            question_list.append({
                "id": q.id,
                "subject": subject_name,
                "number": counter,
                "question": q.question_text,
                "option_a": q.option1,
                "option_b": q.option2,
                "option_c": q.option3,
                "option_d": q.option4,
            })
            counter += 1

    # ---------------------------------------------------------
    return render(request, 'finaltest.html', {
        'subjects': subjects,
        'all_questions': question_list,
        'header_title': header_title, 
        'subject_titles': subject_titles,   # 👉 Send title to template
    })


from django.shortcuts import render, redirect

def start_final_test(request):
    if request.method == "POST":
        # Clear any previous session data related to tests
        for key in ["exam_start_time", "selected_questions", "score", "total_questions", "answers_review", "selected_subject", "final_selected_questions", "final_subject_limits"]:
            request.session.pop(key, None)

        # Redirect to final test page
        return redirect('finaltest')

    return render(request, 'start_final_test.html', {
        "active_page": "start_final_test",
    })


import json
from django.http import JsonResponse

@student_login_required
def submit_final_test(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request"})

    data = json.loads(request.body)
    answers = data.get("answers", [])

    student = get_object_or_404(Student, id=request.session["student_id"])

    score = 0
    attempted_questions = 0
    total_questions = len(answers)

    review_data = []

    for item in answers:
        qid = item.get("id")
        selected_answer = item.get("answer")

        if selected_answer:
            attempted_questions += 1

        try:
            question = FinalQuestion.objects.get(id=qid)
        except FinalQuestion.DoesNotExist:
            continue

        is_correct = selected_answer == question.correct_answer

        if is_correct:
            score += 1

        review_data.append({
            "question": question.question_text,
            "subject": str(question.subject),
            "selected": selected_answer,
            "correct": question.correct_answer,
            "is_correct": is_correct,
        })

    average_percentage = round((score / total_questions) * 100, 2) if total_questions else 0
    remark = "PASS" if average_percentage >= 70 else "FAIL"

    FinalResultHistory.objects.create(
        student=student,
        subject_percentages={},   # you already handle this elsewhere
        average_percentage=average_percentage,
        remark=remark,
        attempted_questions=attempted_questions,
        total_questions=total_questions,
        review_data=review_data,
    )

    return JsonResponse({
        "status": "ok",
        "redirect": "/final-result/"
    })


from .models import FinalResultHistory 


from collections import defaultdict

@student_login_required
def final_result(request):
    student = get_object_or_404(Student, id=request.session["student_id"])

    last_result = FinalResultHistory.objects.filter(
        student=student
    ).order_by('-test_date').first()

    if not last_result:
        messages.warning(request, "No final test results found.")
        return redirect("student_dashboard")

    # ---------- SUBJECT CALCULATION ----------
    subject_map = defaultdict(lambda: {"correct": 0, "total": 0})

    for item in last_result.review_data:
        subject = item["subject"]
        subject_map[subject]["total"] += 1
        if item["is_correct"]:
            subject_map[subject]["correct"] += 1

    subject_results = []
    for subject, data in subject_map.items():
        percentage = round((data["correct"] / data["total"]) * 100, 2)
        subject_results.append({
            "name": subject,
            "percentage": percentage
        })

    context = {
        "student_id": student.id,
        "firstname": student.firstname,
        "lastname": student.lastname,
        "test_date": last_result.test_date,

        "attempted": last_result.attempted_questions,
        "total": last_result.total_questions,

        "subject_results": subject_results,

        "average_percentage": last_result.average_percentage,
        "percentage": last_result.average_percentage,
        "remark": last_result.remark,
        "active_page": "final_result",
    }

    return render(request, "finalresult.html", context)


@student_login_required
def final_result_history(request):
    student = get_object_or_404(Student, id=request.session["student_id"])

    results = FinalResultHistory.objects.filter(
        student=student
    ).order_by('-test_date')

    if not results.exists():
        messages.warning(request, "No final test results found.")
        return redirect("student_dashboard")

    # Attach subject results to each test
    for result in results:
        subject_map = defaultdict(lambda: {"correct": 0, "total": 0})

        for item in result.review_data:
            subject = item["subject"]
            subject_map[subject]["total"] += 1
            if item["is_correct"]:
                subject_map[subject]["correct"] += 1

        subject_results = []
        for subject, data in subject_map.items():
            percentage = round((data["correct"] / data["total"]) * 100, 2)
            subject_results.append({
                "name": subject,
                "percentage": percentage
            })

        result.subject_results = subject_results

    context = {
        "student": student,
        "results": results,
        "active_page": "final_result",
    }

    return render(request, "final_test_history.html", context)


@student_login_required
def final_review(request):
    if 'student_id' not in request.session:
        return redirect('login')

    student = get_object_or_404(Student, id=request.session['student_id'])

    latest_result = FinalResultHistory.objects.filter(
        student=student
    ).order_by('-test_date').first()

    if not latest_result:
        return render(request, "no_review.html")

    return render(request, "final_test_review.html", {
        "student": student,
        "review_data": latest_result.review_data,
        "average_percentage": latest_result.average_percentage,
        "subject_percentages": latest_result.subject_percentages,
        "remark": latest_result.remark,
        "date": latest_result.test_date,
    })

@student_login_required
def final_attempts(request):
    if 'student_id' not in request.session:
        return redirect('login')

    student = Student.objects.get(id=request.session['student_id'])

    # Get all attempts sorted newest first
    attempts = FinalResultHistory.objects.filter(student=student).order_by('-id')

    return render(request, "final_attempts.html", {
        "student": student,
        "attempts": attempts
    })


