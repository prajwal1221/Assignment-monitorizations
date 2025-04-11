from django.utils import timezone

def add_variable_to_context(request):
    return {
        'now': timezone.now(),
    }