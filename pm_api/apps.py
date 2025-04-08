# import threading
# import time
# import datetime
# from django.utils.timezone import now
# from django.apps import AppConfig
# from .models import *
# from .views import mail
# from django.core.exceptions import ObjectDoesNotExist
# import logging

# logger = logging.getLogger(__name__)

# class PmApiConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'pm_api'

#     def ready(self):
#         # Import inside the ready method to avoid AppRegistryNotReady
#         from django.db.models.signals import post_migrate

#         # Start the thread after migrations
#         post_migrate.connect(self.start_reminder_thread, sender=self)

#     def start_reminder_thread(self, **kwargs):
#         # Start the background reminder thread
#         ReminderThread().start()

# class ReminderThread(threading.Thread):
#     def __init__(self):
#         super().__init__()
#         self.daemon = True  # Ensure the thread exits when the main process stops

#     def run(self):
#         while True:
#             try:
#                 self.check_for_reminders()
#             except Exception as e:
#                 logger.error(f"Error in ReminderThread: {e}")
#             time.sleep(24 * 60 * 60)  # Wait for 24 hours before the next check

#     def check_for_reminders(self):
#         # Calculate the target date (4 days from today)
#         target_date = now().date() + datetime.timedelta(minutes=1)

#         # Fetch projects with a release date matching the target date
#         projects = addProject.objects.filter(release_date=target_date)

#         for project in projects:
#             assigned_names = project.assigned_to.split(", ")
#             receiver_emails = []

#             for name in assigned_names:
#                 try:
#                     user = RegistrationIndividual.objects.get(name=name)
#                     receiver_emails.append(user.email)
#                 except ObjectDoesNotExist:
#                     logger.warning(f"User '{name}' not found.")

#             # Add additional recipients if needed
#             additional_emails = ["khushi.sharma@nokia"]
#             receiver_emails.extend(additional_emails)

#             if receiver_emails:
#                 # Email subject and body
#                 subject = f"Reminder: Project '{project.project_name}' is releasing soon!"
#                 body = f"""
#                 <!DOCTYPE html>
#                 <html>
#                 <body>
#                     <p>Dear Team,</p>
#                     <p>This is a reminder that the project <strong>{project.project_name}</strong> is scheduled for release on <strong>{project.release_date.strftime('%d/%m/%Y')}</strong>.</p>
#                     <p>Details of the project:</p>
#                     <ul>
#                         <li><strong>Project Name:</strong> {project.project_name}</li>
#                         <li><strong>Description:</strong> {project.description}</li>
#                         <li><strong>Priority:</strong> {project.priority}</li>
#                         <li><strong>Led By:</strong> {project.led_by}</li>
#                         <li><strong>Assigned By:</strong> {project.assigned_by}</li>
#                         <li><strong>Completion Percentage:</strong> {project.completion_percentage}%</li>
#                     </ul>
#                     <p>Please ensure all tasks are completed before the release date.</p>
#                     <p>Best Regards,<br>Project Management Team</p>
#                 </body>
#                 </html>
#                 """

#                 # Send the email
#                 mail(subject, body, receiver_emails)
#                 logger.info(f"Reminder sent for project '{project.project_name}'")
#             else:
#                 logger.warning(f"No valid email addresses for project '{project.project_name}'")
