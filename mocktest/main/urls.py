from django.urls import path
from . import views

urlpatterns = [

    # ===================== AUTH =====================
    path('', views.student_login, name='login'),
    path('logout/', views.student_logout, name='logout'),
    path('change-password/', views.change_password, name='change_password'),

    # ===================== DASHBOARD =====================
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('progress/', views.student_progress, name='student_progress'),

    # ===================== MCQ TEST =====================
    path('start-test/', views.start_test, name='start_test'),
    path('test/', views.mcq_test, name='mcq_test'),
    path('mock-result/', views.result, name='result'),
    path('review/', views.review, name='review'),
    path('test-history/', views.test_history, name='test_history'),

    # ===================== FINAL TEST =====================
    path('start-final-test/', views.start_final_test, name='start_final_test'),
    path('final-test/', views.finaltest, name='finaltest'),
    path('finaltest/submit/', views.submit_final_test, name='submit_final_test'),

    # ===================== FINAL RESULTS =====================
    path('final-result/', views.final_result, name='final_result'),
    path('final-history/', views.final_result_history, name='final_result_history'),
    path(
        'final-history/<int:result_id>/',
        views.final_attempts,
        name='final_result_history_detail'
    ),
    path('final-review/', views.final_review, name='final_review')
]
