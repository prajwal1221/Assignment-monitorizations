from pyexpat.errors import messages
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Assignment, Submission
from .forms import AssignmentForm, SubmissionForm
from accounts.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from .models import Submission
from .ai_utils import extract_text_from_pdf, grade_submission


@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher():
        return redirect('home')
    assignments = Assignment.objects.filter(teacher=request.user).order_by('-created_at')
    return render(request, 'assignments/teacher_dashboard.html', {'assignments': assignments})

@login_required
def student_dashboard(request):
    if not request.user.is_student():
        return redirect('home')
    assignments = Assignment.objects.all().order_by('-created_at')
    submissions = Submission.objects.filter(student=request.user)
    submitted_assignments = [sub.assignment.id for sub in submissions]
    
    context = {
        'assignments': assignments,
        'submissions': submissions,
        'submitted_assignments': submitted_assignments,
    }
    return render(request, 'assignments/student_dashboard.html', context)

@login_required
def create_assignment(request):
    if not request.user.is_teacher():
        return redirect('home')
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.teacher = request.user
            assignment.save()

            # Fetch all student emails
            students = User.objects.filter(user_type='student')
            emails = [student.email for student in students if student.email]

            # Send email to students
            send_mail(
                subject=f"New Assignment Posted: {assignment.title}",
                message=f"Dear Student,\n\nA new assignment has been posted by {request.user.username}.\n\n"
                        f"Title: {assignment.title}\n"
                        f"Description: {assignment.description}\n"
                        f"Deadline: {assignment.deadline.strftime('%Y-%m-%d %H:%M')}\n\n"
                        f"Please log in to the portal to view and submit it.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=emails,
                fail_silently=False,
            )

            return redirect('teacher_dashboard')
    else:
        form = AssignmentForm()
    
    return render(request, 'assignments/create_assignment.html', {'form': form})

@login_required
def view_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    
    if request.user.is_student():
        submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
        can_submit = timezone.now() <= assignment.deadline
        
        if request.method == 'POST' and can_submit:
            form = SubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                new_submission = form.save(commit=False)
                new_submission.assignment = assignment
                new_submission.student = request.user
                
                if submission:  # Update existing submission
                    submission.file = new_submission.file
                    submission.submitted_at = timezone.now()
                    submission.save()
                else:  # Create new submission
                    new_submission.save()
                    
                return redirect('student_dashboard')
        else:
            form = SubmissionForm()
            
        context = {
            'assignment': assignment,
            'submission': submission,
            'form': form,
            'can_submit': can_submit,
        }
        return render(request, 'assignments/view_assignment_student.html', context)
    
    else:  # Teacher view
        submissions = Submission.objects.filter(assignment=assignment)
        return render(request, 'assignments/view_assignment_teacher.html', {
            'assignment': assignment,
            'submissions': submissions,
        })

@login_required
def grade_submission(request, submission_id):
    if not request.user.is_teacher():
        return redirect('home')
        
    submission = get_object_or_404(Submission, pk=submission_id)
    
    if request.method == 'POST':
        grade = request.POST.get('grade')
        comments = request.POST.get('comments')
        
        submission.grade = grade
        submission.comments = comments
        submission.save()
        
        return redirect('view_assignment', pk=submission.assignment.pk)
        
    return render(request, 'assignments/grade_submission.html', {'submission': submission})


def assess_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)

    if request.method == 'POST' and 'grade_with_ai' in request.POST:
        # Extract text from the submitted PDF
        extracted_text = extract_text_from_pdf(submission)

        # Grade the submission using the AI function
        ai_grade = grade_submission(extracted_text)

        # Save the AI-generated grade to the submission
        submission.grade = ai_grade
        submission.save()

        # Provide feedback to the user
        messages.success(request, f'AI grading completed. Grade: {ai_grade}')

    return render(request, 'assess_submission.html', {'submission': submission})

from django.shortcuts import get_object_or_404, redirect
from .models import Submission
from .ai_utils import extract_text_from_pdf, grade_submission

def grade_submission_ai(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)

    if request.method == 'POST':
        # Extract text from the submitted PDF
        extracted_text = extract_text_from_pdf(submission)

        # Grade the submission using the AI function
        ai_grade = grade_submission(extracted_text)

        # Save the AI-generated grade to the submission
        submission.grade = ai_grade
        submission.save()

        # Redirect back to the assignment view or appropriate page
        return redirect('view_assignment', pk=submission.assignment.pk)
