from django.urls import path
from . import views

urlpatterns = [
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('create/', views.create_assignment, name='create_assignment'),
    path('view/<int:pk>/', views.view_assignment, name='view_assignment'),
    path('grade/<int:submission_id>/', views.grade_submission, name='grade_submission'),
    path('grade-submission-ai/<int:submission_id>/', views.grade_submission_ai, name='grade_submission_ai'),
]