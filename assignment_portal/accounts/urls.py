from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/login/', views.login_view, name='login'),  # Custom login view
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/student/', views.StudentSignUpView.as_view(), name='student_signup'),
    path('signup/teacher/', views.TeacherSignUpView.as_view(), name='teacher_signup'),
]