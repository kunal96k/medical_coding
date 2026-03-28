from django.urls import path,include
from django.contrib import admin
from . import views
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('', views.admin_login, name='adminpanel_login'),
    path('admin-dashboard/', views.dashboard, name='adminpanel_dashboard'),
    path('logout/', views.admin_logout, name='adminpanel_logout'),
    path('students/', views.student_list, name='adminpanel_students'),
    path('subjects/', views.subject_list, name='adminpanel_subjects'),
    path('questions/', views.question_list, name='adminpanel_questions'),
    path('add_student/', views.add_student, name='adminpanel_add_student'),
    path("student/<str:username>/results/", views.student_result_history, name="student_result_history"),
    path('edit_student/<int:student_id>/', views.edit_student, name='adminpanel_edit_student'),
    path('delete_student/<int:student_id>/', views.delete_student, name='adminpanel_delete_student'),
    path("upload-fixture/", views.upload_fixture, name="upload_fixture"),
    path("upload_final_fixture/", views.upload_final_fixture, name="upload_final_fixture"),
    path('questions/edit/<int:id>/', views.edit_question, name='edit_question'),
    path('questions/delete/<int:id>/', views.delete_question, name='delete_question'),
    path("final-questions/", views.final_question_list, name="final_question_list"),
    path("final-questions/edit/<int:id>/", views.edit_final_question, name="edit_final_question"),
    path("final-questions/delete/<int:id>/", views.delete_final_question, name="delete_final_question"),
    path("adminpanel/mock-results/", views.mock_result_list, name="mock_result_list"),
    path("adminpanel/final-results/", views.final_result_list, name="final_result_list"),
    path("final-results/<int:result_id>/", views.final_result_history, name="final_result_history"),
    path("final-review/<int:result_id>/",views.admin_final_review,name="final_review"),


]   
