from django.db import models

class Student(models.Model):
    firstname = models.CharField(max_length=100, null=True, blank=True)
    lastname = models.CharField(max_length=100, null=True, blank=True)
    middlename=models.CharField(max_length=100,null=True,blank=True,default="Na")
    student_id = models.CharField(max_length=20, unique=True, editable=False, null=True, blank=True)
    user_id = models.CharField(max_length=255, unique=True, editable=False, null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    has_changed_password = models.BooleanField(default=False)  

    def save(self, *args, **kwargs):
        if not self.student_id:  
            last_student = Student.objects.order_by('-id').first()
            if last_student and last_student.student_id:
                last_number = int(last_student.student_id.replace("MCS", ""))
                new_number = last_number + 1
            else:
                new_number = 1
            self.student_id = f"MCS{new_number:03d}" 

        
        if not self.user_id:
            self.user_id = f"{self.firstname}{self.lastname}".lower()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_id} - {self.user_id}"


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField(unique=True)
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.subject.name} - {self.question_text[:50]}"


class TestResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    date_taken = models.DateTimeField(auto_now_add=True)
    attempt_no = models.IntegerField(default=1)

    @property
    def percentage(self):
        if self.total_questions > 0:
            return (self.score / 30) * 100
        return 0

    @property
    def remark(self):
        pct = self.percentage
        if pct >= 70:
            return "PASS"
        else:
            return "FAIL"

    def __str__(self):
        return f"{self.student} - {self.subject} ({self.score}/{self.total_questions})"

class FinalQuestion(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="final_questions")
    question_text = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.subject.name} - {self.question_text[:50]}"


        # models.py

from django.db import models
from django.db.models import JSONField

 # If using PostgreSQL

class FinalResultHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject_percentages = models.JSONField()
    average_percentage = models.FloatField()
    remark = models.CharField(max_length=10)
    test_date = models.DateTimeField(auto_now_add=True)

    attempted_questions = models.IntegerField()
    total_questions = models.IntegerField()

    review_data = models.JSONField()

    def __str__(self):
        return f"{self.student.firstname} {self.student.lastname} - {self.test_date.date()}"

