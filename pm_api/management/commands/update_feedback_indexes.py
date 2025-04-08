from django.core.management.base import BaseCommand
from pm_api.models import Feedback  # Replace 'your_app' with your actual app name

class Command(BaseCommand):
    help = 'Updates project-specific indexes for existing feedback entries'

    def handle(self, *args, **options):
        projects = set(Feedback.objects.values_list('project', flat=True))
        
        for project_id in projects:
            feedbacks = Feedback.objects.filter(project_id=project_id).order_by('id')
            for index, feedback in enumerate(feedbacks, start=1):
                feedback.project_index = index
                feedback.save(update_fields=['project_index'])
                self.stdout.write(f'Updated feedback {feedback.id} with project_index {index}')