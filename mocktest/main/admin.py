from django.contrib import admin
from .models import Student, Subject, Question, TestResult,FinalQuestion,FinalResultHistory

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id','firstname','lastname','user_id')
    search_fields = ('student_id', 'password', 'firstname', 'lastname', 'user_id',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('subject', 'question_text', 'correct_answer')
    search_fields = ('question_text',)
    list_filter = ('subject',)

@admin.register(FinalQuestion)
class FinalQuestionAdmin(admin.ModelAdmin):
    list_display = ('subject', 'question_text', 'correct_answer')
    search_fields = ('question_text',)
    list_filter = ('subject',)

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'subject',
        'score',
        'total_questions',
        'attempt_no',
        'date_taken',
        'percentage',
        'remark',
    )
    search_fields = ('student__student_id', 'student__firstname', 'student__lastname', 'subject__name')
    list_filter = ('subject', 'attempt_no', 'date_taken')

    # Custom method for percentage
    def percentage(self, obj):
        if obj.total_questions > 0:
            return f"{(obj.score / 30) * 100:.2f}%"
        return "0%"

    percentage.short_description = "Percentage"

    # Custom method for remark with passing criteria = 70%
    def remark(self, obj):
        pct = (obj.score / 30) * 100
        if pct >= 70:
            return "Pass"
        else:
            return "Fail"

    remark.short_description = "Remark"

@admin.register(FinalResultHistory)
class FinalResultHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'student_name',
        'subject_percentages',
        'average_percentage',
        'remark',
        'test_date',
    )
    search_fields = (
        'student__firstname',
        'student__lastname',
        'student__student_id',
    )
    list_filter = ('remark', 'test_date')

    # Display student full name
    def student_name(self, obj):
        return f"{obj.student.firstname} {obj.student.lastname}"
    student_name.short_description = "Student"

    # Improve formatting
    def average_percentage(self, obj):
        return f"{obj.average_percentage:.2f}%"
    average_percentage.short_description = "Average %"
