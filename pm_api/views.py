from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import addProject,RegistrationIndividual,RegistrationTeam ,Bug, Feedback,Comment,Dailyprogress,LatestUpdate, Version
from .serializers import AddProjectSerializer,RegistrationIndividualSerializer,RegistrationTeamSerializer,BugSerializer,FeedbackSerializer,DailyProgressSerializer,LatestUpdateSerializer,AssignedPeopleSerializer, CommentSerializer, VersionSerializer
from datetime import date
from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.hashers import make_password
from rest_framework import viewsets
import smtplib
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import logging
from django.utils import timezone



logger = logging.getLogger(__name__)

class AddProjectAPIView(APIView):

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk:
            # Fetch a specific project by ID
            try:
                project = addProject.objects.get(pk=pk)
                serializer = AddProjectSerializer(project)
                
                return Response(serializer.data, status=status.HTTP_200_OK)
            except addProject.DoesNotExist:
                return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Fetch all projects
            projects = addProject.objects.all()
            serializer = AddProjectSerializer(projects, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
 
    def post(self, request, *args, **kwargs):
        try:
            serializer = AddProjectSerializer(data=request.data)
            if serializer.is_valid():
                # Save the project details
                project = serializer.save()

                # Extract assigned names and fetch emails
                assigned_names = request.data.get('assigned_to', '').strip()
                assigned_names_list = [name.strip() for name in assigned_names.split(',')] if assigned_names else []

                receiver_emails = []
                for name in assigned_names_list:
                    try:
                        user = RegistrationIndividual.objects.get(name=name)
                        receiver_emails.append(user.email)
                    except ObjectDoesNotExist:
                        logger.warning(f"User with name '{name}' does not exist in the database.")

                additional_emails = ["shiv.sahu@nokia.com", "anil.3.kumar@nokia.com"]
                receiver_emails.extend(additional_emails)

                if receiver_emails:
                    subject = f"New Project Assigned: {project.project_name}"
                    body = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                            h2 {{
                                font-size: 20px;
                                color: #333;
                            }}
                            p {{
                                font-size: 14px;
                                color: black;
                                margin: 5px 0;
                                line-height: 1.2;
                            }}
                            .bold {{
                                font-weight: bold;
                            }}
                            .section {{
                                margin-bottom: 20px;
                            }}
                        </style>
                    </head>
                    <body>
                        <p>Dear Team,</p>

                        <p>A new project has been added on the Project Management System.Below are the details of the project for your reference:</p>

                        <div class="section">
                            <h2>Project Details</h2>
                            <p><span class="bold">Project Name:</span> {project.project_name}</p>
                            <p><span class="bold">Description:</span> {project.description}</p>
                            <p><span class="bold">Priority:</span> {project.priority}</p>
                            <p><span class="bold">Led By:</span> {project.led_by}</p>
                            <p><span class="bold">Assigned By:</span> {project.assigned_by}</p>
                            <p><span class="bold">Assigned To:</span> {project.assigned_to}</p>
                            <p><span class="bold">Current Milestone:</span> {project.current_milestone}</p>
                            <p><span class="bold">Completion Percentage:</span> {project.completion_percentage}%</p>
                            <p><span class="bold">Completed:</span> {"Yes" if project.completed else "No"}</p>
                        </div>

                        <div class="section">
                            <h2>Deadlines & Efforts</h2>
                            <p><span class="bold">Research Deadline:</span> {project.research_deadline.strftime('%d/%m/%Y')}</p>
                            <p><span class="bold">Effort:</span> {project.research_effort}%</p>
                            <p><span class="bold">Design Deadline:</span> {project.design_deadline.strftime('%d/%m/%Y')}</p>
                            <p><span class="bold">Effort:</span> {project.design_effort}%</p>
                            <p><span class="bold">Development Deadline:</span> {project.development_deadline.strftime('%d/%m/%Y')}</p>
                            <p><span class="bold">Effort:</span> {project.development_effort}%</p>
                            <p><span class="bold">Testing Deadline:</span> {project.testing_deadline.strftime('%d/%m/%Y')}</p>
                            <p><span class="bold">Effort:</span> {project.testing_effort}%</p>
                            <p><span class="bold">Release Date:</span> {project.release_date.strftime('%d/%m/%Y')}</p>
                        </div>

                        <div class="section">
                            <h2>Review Schedule</h2>
                            <p><span class="bold">Review Day:</span> {project.review}</p>
                        </div>

                        <p>Please review the details and reach out if you have any questions or need further clarification.</p>

                        <p>Best Regards,<br>Project Management Team</p>
                    </body>
                    </html>
                    """

                    mail(subject, body, receiver_emails)
                else:
                    logger.warning("No valid email addresses found to send the notification.")
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if not pk:
            return Response({"error": "Project ID is required for updating."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = addProject.objects.get(pk=pk)
        except addProject.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        old_data = AddProjectSerializer(project).data  # Get the current data before updating
        serializer = AddProjectSerializer(project, data=request.data, partial=True)  # Allow partial updates
        

        if serializer.is_valid():
            updated_project = serializer.save()  # Save the updates
            new_data = request.data  # Get the updated data
            # Identify changes and prepare email content
            changes = []
            for field, old_value in old_data.items():
                new_value = new_data.get(field)
                field = str(",".join(field.split('_'))).upper()
                if old_value != new_value and new_value not in [None, ""]:

                    changes.append(f"<p><strong>{field}:</strong><br> <strong>Previous Value: </strong>{old_value} <br><br> <strong>New value: </strong>{new_value}</p>")
                    

            if changes:
                subject = f"Project Updated: {updated_project.project_name}"
                body = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    
                <body>
                    <p>Dear Team,</p>
                    <p>The following changes have been made to the project <strong>{updated_project.project_name}</strong>:</p>
                    {"".join(changes)}
                    <p>Best Regards,<br>Project Management Team</p>
                </body>
                </html>
                """

                # Get email recipients
                assigned_names = updated_project.assigned_to.split(", ")
                receiver_emails = []

                for name in assigned_names:
                    try:
                        user = RegistrationIndividual.objects.get(name=name)
                        receiver_emails.append(user.email)
                    except ObjectDoesNotExist:
                        logger.warning(f"User with name '{name}' does not exist in the database.")

                additional_emails = ["shiv.sahu@nokia.com","anil.3.kumar@nokia.com"]
                receiver_emails.extend(additional_emails)

                # Send the email if there are recipients
                if receiver_emails:
                    mail(subject, body, receiver_emails)
                    

            
            return Response(request.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.db.models import Count, Q
from datetime import date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class VersionAPIView(APIView):
    def get(self,request):
        version_number = Version.objects.all()
        serializer = VersionSerializer(version_number,many=True)
        return Response(serializer.data)

class QuickInsightsAPIView(APIView):
    def get(self, request):
        # Total projects
        total_projects = addProject.objects.count()

        # Completed projects
        completed_projects = addProject.objects.filter(completed=True).count()

        # Most open feedbacks (Project with the highest number of open feedbacks)
        # Here we assume open feedback means is_added == False.
        most_open_feedbacks_project = addProject.objects.annotate(
            open_feedback_count=Count('project_feedback', filter=Q(project_feedback__is_added=False))
        ).order_by('-open_feedback_count').first()
        most_open_feedbacks_info = {
            "name": most_open_feedbacks_project.project_name if most_open_feedbacks_project else None,
            "open_feedbacks": most_open_feedbacks_project.open_feedback_count if most_open_feedbacks_project else 0,
        }

        # Upcoming release
        upcoming_release = addProject.objects.filter(release_date__gte=date.today()).order_by('release_date').first()
        upcoming_release_info = {
            "name": upcoming_release.project_name if upcoming_release else None,
            "days_left": (upcoming_release.release_date - date.today()).days if upcoming_release else None,
        }

        # Bar graph data (project name vs completion percentage)
        bar_graph_data = [
            {"name": project.project_name, "completion_percentage": project.completion_percentage}
            for project in addProject.objects.all()
        ]

        # Return all insights
        data = {
            "total_projects": total_projects,
            "completed_projects": completed_projects,
            "most_open_feedbacks": most_open_feedbacks_info,
            "upcoming_release": upcoming_release_info,
            "bar_graph_data": bar_graph_data,
        }
        return Response(data, status=status.HTTP_200_OK)


class BugAPIView(APIView):
    def get(self, request, project_id=None,*args,**kwargs):
        pk = kwargs.get('pk')
        if project_id:
            # Retrieve all bugs related to a specific project
            bugs = Bug.objects.filter(project_id=project_id)
            bugs_serializer = BugSerializer(bugs, many=True)

            return Response({
                "bugs": bugs_serializer.data
            }, status=status.HTTP_200_OK)
        elif pk:
        
            # Fetch a specific project by ID
            try:
                bug = Bug.objects.get(pk=pk)
                serializer = BugSerializer(bug)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Bug.DoesNotExist:
                return Response({"Bug": []}, status=status.HTTP_200_OK)
        else:
            # Fetch all projects
            bugs = Bug.objects.all()
            serializer = BugSerializer(bugs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
    def post(self, request, *args, **kwargs):
        serializer = BugSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the new project
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        try:
            bug = Bug.objects.get(pk=pk)
        except Bug.DoesNotExist:
            return Response({"error": "Bug not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BugSerializer(bug, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        try:
            bug = Bug.objects.get(pk=pk)
        except Bug.DoesNotExist:
            return Response({"error": "Bug not found"}, status=status.HTTP_404_NOT_FOUND)
        bug.delete()
        return Response({"message": "Bug deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

from django.utils import timezone
import pytz
import logging

logger = logging.getLogger(__name__)

class FeedbackNotificationService:
    @staticmethod
    def convert_to_ist(utc_time):
        """Convert UTC time to IST."""
        ist = pytz.timezone('Asia/Kolkata')
        if timezone.is_naive(utc_time):
            utc_time = timezone.make_aware(utc_time, pytz.UTC)
        return utc_time.astimezone(ist)

    @staticmethod
    def format_ist_time(utc_time):
        """Format UTC time to IST string."""
        ist_time = FeedbackNotificationService.convert_to_ist(utc_time)
        return ist_time.strftime('%d/%m/%Y %I:%M %p IST')

    @staticmethod
    def get_receiver_emails(project):
        """Get list of receiver emails based on project assignments and additional stakeholders."""
        receiver_emails = []
        
        # Get assigned names from the project
        assigned_names = project.assigned_to.split(',') if project.assigned_to else []
        
        # Get emails for assigned users
        for name in assigned_names:
            try:
                user = RegistrationIndividual.objects.get(name=name.strip())
                receiver_emails.append(user.email)
            except ObjectDoesNotExist:
                logger.warning(f"User with name '{name}' does not exist in the database.")
        
        # Add additional stakeholder emails
        additional_emails = ["shiv.sahu@nokia.com", "anil.3.kumar@nokia.com"]
        receiver_emails.extend(additional_emails)
        
        return receiver_emails

    @staticmethod
    def send_new_feedback_notification(feedback):
        """Send email notification for new feedback."""
        try:
            project = feedback.project
            receiver_emails = FeedbackNotificationService.get_receiver_emails(project)
            
            if not receiver_emails:
                logger.warning("No valid email addresses found to send the notification.")
                return
            
            # Convert posting time to IST
            ist_time = FeedbackNotificationService.format_ist_time(feedback.posting_time)
            
            subject = f"New Feedback Added: {project.project_name}"
            body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    h2 {{
                        font-size: 20px;
                        color: #333;
                    }}
                    p {{
                        font-size: 14px;
                        color: black;
                        margin: 5px 0;
                        line-height: 1.2;
                    }}
                    .bold {{
                        font-weight: bold;
                    }}
                    .section {{
                        margin-bottom: 20px;
                    }}
                </style>
            </head>
            <body>
                <p>Dear Team,</p>

                <p>New feedback has been added for project {project.project_name}.</p>

                <div class="section">
                    <h2>Feedback Details</h2>
                    <p><span class="bold">Project:</span> {project.project_name}</p>
                    <p><span class="bold">Posted By:</span> {feedback.posted_by}</p>
                    <p><span class="bold">Description:</span> {feedback.feedback_description}</p>
                    <p><span class="bold">Deadline:</span> {feedback.deadline}</p>
                    <p><span class="bold">Created At:</span> {ist_time}</p>
                </div>

                <p>Please review the feedback and take necessary actions.</p>

                <p>Best Regards,<br>Project Management Team</p>
            </body>
            </html>
            """
            
            mail(subject, body, receiver_emails)
            logger.info(f"New feedback notification sent successfully for project {project.project_name}")
            
        except Exception as e:
            logger.error(f"Error sending new feedback notification: {str(e)}")
            raise

    @staticmethod
    def send_feedback_update_notification(feedback, old_data, new_data):
        """Send email notification for feedback updates."""
        try:
            project = feedback.project
            receiver_emails = FeedbackNotificationService.get_receiver_emails(project)
            
            if not receiver_emails:
                logger.warning("No valid email addresses found to send the notification.")
                return
            
            # Convert posting time to IST
            ist_time = FeedbackNotificationService.format_ist_time(feedback.posting_time)
            
            # Identify changes
            changes = []
            for field, old_value in old_data.items():
                new_value = new_data.get(field)
                if new_value is not None and str(old_value) != str(new_value):
                    field_name = str(" ".join(field.split('_'))).upper()
                    changes.append(f"<p><strong>{field_name}:</strong><br> <strong>Previous Value: </strong>{old_value} <br><br> <strong>New value: </strong>{new_value}</p>")
            
            if not changes:
                logger.info("No changes detected in feedback update")
                return
            
            subject = f"Feedback Updated: {project.project_name}"
            body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    h2 {{
                        font-size: 20px;
                        color: #333;
                    }}
                    p {{
                        font-size: 14px;
                        color: black;
                        margin: 5px 0;
                        line-height: 1.2;
                    }}
                    .bold {{
                        font-weight: bold;
                    }}
                    .section {{
                        margin-bottom: 20px;
                    }}
                </style>
            </head>
            <body>
                <p>Dear Team,</p>

                <p>The following changes have been made to the feedback for project <strong>{project.project_name}</strong> at {ist_time}:</p>

                <div class="section">
                    <h2>Changes Made</h2>
                    {"".join(changes)}
                </div>

                <div class="section">
                    <h2>Feedback Details</h2>
                    <p><span class="bold">Project:</span> {project.project_name}</p>
                    <p><span class="bold">Posted By:</span> {feedback.posted_by}</p>
                    <p><span class="bold">Description:</span> {feedback.feedback_description}</p>
                    <p><span class="bold">Deadline:</span> {feedback.deadline}</p>
                </div>

                <p>Please review these changes and take any necessary actions.</p>

                <p>Best Regards,<br>Project Management Team</p>
            </body>
            </html>
            """
            
            mail(subject, body, receiver_emails)
            logger.info(f"Feedback update notification sent successfully for project {project.project_name}")
            
        except Exception as e:
            logger.error(f"Error sending feedback update notification: {str(e)}")
            raise

    @staticmethod
    def send_comment_notification(feedback, comment):
        """Send email notification for new comments."""
        try:
            project = feedback.project
            receiver_emails = FeedbackNotificationService.get_receiver_emails(project)
            
            if not receiver_emails:
                logger.warning("No valid email addresses found to send the comment notification.")
                return
            
            # Convert posting time to IST
            ist_time = FeedbackNotificationService.format_ist_time(comment.posting_time)
            
            subject = f"New Comment Added: {project.project_name}"
            body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    h2 {{
                        font-size: 20px;
                        color: #333;
                    }}
                    p {{
                        font-size: 14px;
                        color: black;
                        margin: 5px 0;
                        line-height: 1.2;
                    }}
                    .bold {{
                        font-weight: bold;
                    }}
                    .section {{
                        margin-bottom: 20px;
                    }}
                </style>
            </head>
            <body>
                <p>Dear Team,</p>

                <p>A new comment has been added to feedback for project {project.project_name}.</p>

                <div class="section">
                    <h2>Comment Details</h2>
                    <p><span class="bold">Project:</span> {project.project_name}</p>
                    <p><span class="bold">Posted By:</span> {comment.posted_by}</p>
                    <p><span class="bold">Comment:</span> {comment.content}</p>
                    <p><span class="bold">Posted At:</span> {ist_time}</p>
                </div>

                <div class="section">
                    <h2>Original Feedback</h2>
                    <p><span class="bold">Posted By:</span> {feedback.posted_by}</p>
                    <p><span class="bold">Description:</span> {feedback.feedback_description}</p>
                </div>

                <p>Please review this comment and take any necessary actions.</p>

                <p>Best Regards,<br>Project Management Team</p>
            </body>
            </html>
            """
            
            mail(subject, body, receiver_emails)
            logger.info(f"Comment notification sent successfully for project {project.project_name}")
            
        except Exception as e:
            logger.error(f"Error sending comment notification: {str(e)}")
            raise


class FeedbackAPIView(APIView):
    def get(self, request, project_id=None, username = None,*args, **kwargs):
        pk = kwargs.get('pk')
        if project_id:
            feedbacks = Feedback.objects.filter(project_id=project_id)
            feedback_data = []
            for feedback in feedbacks:
                feedback_serializer = FeedbackSerializer(feedback)
                comments = Comment.objects.filter(feedback=feedback)
                comments_serializer = CommentSerializer(comments, many=True)
                feedback_dict = feedback_serializer.data
                feedback_dict['comments'] = comments_serializer.data
                feedback_data.append(feedback_dict)
            
            return Response({"feedbacks": feedback_data}, status=status.HTTP_200_OK)
        
        elif username:
            feedbacks = Feedback.objects.filter(assigned_to = username)
            feedback_data = []
            for feedback in feedbacks:
                feedback_serializer = FeedbackSerializer(feedback)
                comments = Comment.objects.filter(feedback=feedback)
                comments_serializer = CommentSerializer(comments, many=True)
                feedback_dict = feedback_serializer.data
                feedback_dict['comments'] = comments_serializer.data
                feedback_data.append(feedback_dict)
            
            return Response({"feedbacks": feedback_data}, status=status.HTTP_200_OK)
        
        elif pk:
            try:
                feedback = Feedback.objects.get(pk=pk)
                comments = Comment.objects.filter(feedback=feedback)
                comments_serializer = CommentSerializer(comments, many=True)
                feedback_serializer = FeedbackSerializer(feedback)
                response_data = feedback_serializer.data
                response_data['comments'] = comments_serializer.data
                return Response(response_data, status=status.HTTP_200_OK)
            except Feedback.DoesNotExist:
                return Response({"Feedback": []}, status=status.HTTP_200_OK)
        
        else:
            feedbacks = Feedback.objects.all()
            feedbacks_serializer = FeedbackSerializer(feedbacks, many=True)
            return Response(feedbacks_serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        if 'feedback_id' in request.data and 'content' in request.data:
            try:
                feedback = Feedback.objects.get(pk=request.data['feedback_id'])
                comment = feedback.add_comment(
                    content=request.data['content'],
                    posted_by=request.data.get('posted_by', 'Anonymous')
                )
                
                try:
                    FeedbackNotificationService.send_comment_notification(feedback, comment)
                except Exception as e:
                    logger.error(f"Error sending comment notification: {str(e)}")
                
                comment_serializer = CommentSerializer(comment)
                feedback_serializer = FeedbackSerializer(feedback)
                response_data = feedback_serializer.data
                response_data['comments'] = [comment_serializer.data]

                return Response(response_data, status=status.HTTP_201_CREATED)
            except Feedback.DoesNotExist:
                return Response({"error": "Feedback not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = FeedbackSerializer(data=request.data)
            if serializer.is_valid():
                feedback = serializer.save()
                
                try:
                    FeedbackNotificationService.send_new_feedback_notification(feedback)
                except Exception as e:
                    logger.error(f"Error sending feedback notification: {str(e)}")
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        try:
            if pk is None:
                pk = request.data.get('id')
                if pk is None:
                    return Response({"error": "Feedback ID is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            feedback = Feedback.objects.get(pk=pk)
            old_data = FeedbackSerializer(feedback).data
            serializer = FeedbackSerializer(feedback, data=request.data, partial=True)
            
            if serializer.is_valid():
                updated_feedback = serializer.save()
                
                try:
                    FeedbackNotificationService.send_feedback_update_notification(
                        updated_feedback,
                        old_data,
                        request.data
                    )
                except Exception as e:
                    logger.error(f"Error sending update notification: {str(e)}")
                
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Feedback.DoesNotExist:
            return Response({"error": f"Feedback not found with ID: {pk}"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Unexpected error in feedback update: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CommentAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # This is for posting comments
        if 'feedback_id' in request.data and 'content' in request.data:
            try:
                feedback = Feedback.objects.get(pk=request.data['feedback_id'])
                comment = Comment.objects.create(
                    feedback=feedback,
                    content=request.data['content'],
                    posted_by=request.data.get('posted_by', 'Anonymous'),
                )
                comment_serializer = CommentSerializer(comment)
                project = feedback.project
                assigned_names = project.assigned_to.split(',') if project.assigned_to else []
                receiver_emails = []
                
                for name in assigned_names:
                    try:
                        user = RegistrationIndividual.objects.get(name=name.strip())
                        receiver_emails.append(user.email)
                    except ObjectDoesNotExist:
                        logger.warning(f"User with name '{name}' does not exist in the database.")
                
                additional_emails = ["shiv.sahu@nokia.com", "anil.3.kumar@nokia.com"]
                receiver_emails.extend(additional_emails)
                if receiver_emails:
                    subject = f"New Comment Added: Feedback on {project.project_name}"
                    body = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                            h2 {{
                                font-size: 20px;
                                color: #333;
                            }}
                            p {{
                                font-size: 14px;
                                color: black;
                                margin: 5px 0;
                                line-height: 1.2;
                            }}
                            .bold {{
                                font-weight: bold;
                            }}
                            .section {{
                                margin-bottom: 20px;
                            }}
                        </style>
                    </head>
                    <body>
                        <p>Dear Team,</p>

                        <p>A new comment has been added to feedback for project {project.project_name}.</p>

                        <div class="section">
                            <h2>Comment Details</h2>
                            <p><span class="bold">Comment By:</span> {comment.posted_by}</p>
                            <p><span class="bold">Comment:</span> {comment.content}</p>
                            <p><span class="bold">Posted At:</span> {timezone.localtime(comment.posting_time).strftime('%d/%m/%Y %H:%M')}</p>

                        </div>

                        <div class="section">
                            <h2>Original Feedback</h2>
                            <p><span class="bold">Feedback:</span> {feedback.project_index}</p>
                            <p><span class="bold">Posted By:</span> {feedback.posted_by}</p>
                            <p><span class="bold">Description:</span> {feedback.feedback_description}</p>
                            <p><span class="bold">Bug Report:</span> {feedback.is_bug}</p>
                            <p><span class="bold">Assigned To:</span> {feedback.assigned_to}</p>



                        <p>Please review the comment and take necessary actions.</p>

                        <p>Best Regards,<br>Project Management Team</p>
                    </body>
                    </html>
                    """
                    
                    mail(subject, body, receiver_emails)
                
                return Response(comment_serializer.data, status=status.HTTP_201_CREATED)
            except Feedback.DoesNotExist:
                return Response({"error": "Feedback not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Feedback ID and content are required"}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    def post(self, request):
       
        # Retrieve username and password from request
        username = request.data.get('username')
        password = request.data.get('password')

        # Authenticate the user
        user = authenticate(username=username, password=password)

        if user:
            # Generate or retrieve an authentication token for the user
            token, _ = Token.objects.get_or_create(user=user)

            # Retrieve the user's groups
            groups = user.groups.values_list('name', flat=True)  # List of group names

            return Response({
                'message': 'Login successful',
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'groups': list(groups),  
            }, status=status.HTTP_200_OK)
        else:
            # Return an error response for invalid credentials
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request):
        
        # Apply authentication
        self.authentication_classes = [TokenAuthentication]
        self.permission_classes = [IsAuthenticated]

        # Get the currently authenticated user
        user = request.user

        # Retrieve the user's groups
        groups = user.groups.values_list('name', flat=True)  # List of group names

        return Response({
            'user_id': user.id,  # Django's default ID field
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'groups': list(groups),  # Convert QuerySet to list
        }, status=status.HTTP_200_OK)


from django.db.models import Q

import re
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

class RegistrationIndividualAPIView(APIView):
    def get(self, request, pk=None):
        if pk:
            individual = RegistrationIndividual.objects.get(pk=pk)
            serializer = RegistrationIndividualSerializer(individual)

            # Build a regex that matches the individual's name in a comma-separated list.
            # This regex will match the name if it is at the start, in the middle, or at the end,
            # allowing for spaces around the commas.
            regex = r'(^|\s*,\s*)' + re.escape(individual.name) + r'(\s*,\s*|$)'
            total_feedbacks = Feedback.objects.filter(
                assigned_to__regex=regex
            ).count()

            data = serializer.data
            data['total_feedbacks'] = total_feedbacks
            return Response(data, status=status.HTTP_200_OK)
            
        else:
            individuals = RegistrationIndividual.objects.all()
            serialized_data = []

            for individual in individuals:
                serializer = RegistrationIndividualSerializer(individual)
                regex = r'(^|\s*,\s*)' + re.escape(individual.name) + r'(\s*,\s*|$)'
                total_feedbacks = Feedback.objects.filter(
                    assigned_to__regex=regex
                ).count()
                
                data = serializer.data
                data['total_feedbacks'] = total_feedbacks
                serialized_data.append(data)

            return Response(serialized_data, status=status.HTTP_200_OK)


class RegistrationTeamAPIView(APIView):
    def get(self, request, pk=None):
        if pk:
            # Fetch a specific team by ID
            try:
                team = RegistrationTeam.objects.get(pk=pk)
                serializer = RegistrationTeamSerializer(team)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except RegistrationTeam.DoesNotExist:
                return Response({"error": "Team not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Fetch all teams
            teams = RegistrationTeam.objects.all()
            serializer = RegistrationTeamSerializer(teams, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = RegistrationTeamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DailyProgressAPIView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None, project_id=None):
        if project_id:
            # Fetch the project details using project_id
            try:
                project = addProject.objects.get(id=project_id)
            except addProject.DoesNotExist:
                return Response({"project does not exist"}, status=status.HTTP_200_OK)

            # Get the assigned_to field and split it into individual names
            assigned_to = project.assigned_to.split(", ")
            
            # Fetch daily progress of all users linked to the project
            daily_progress = Dailyprogress.objects.filter(
                name__in=assigned_to,  # Match user_name in Dailyprogress with names in assigned_to
                project_id=project_id       # Ensure the progress belongs to the project
            ).order_by("-date")
            
            if daily_progress.exists():
                serializer = DailyProgressSerializer(daily_progress, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"message": "No progress found for this project."}, status=status.HTTP_200_OK)

        elif user_id:
            # Fetch progress specific to a user ID from the URL
            daily_progress = Dailyprogress.objects.filter(user_id=user_id).order_by("-date")
            serializer = DailyProgressSerializer(daily_progress, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            # Fetch daily progress of all users
            daily_progress = Dailyprogress.objects.all().order_by("-date")
            serializer = DailyProgressSerializer(daily_progress, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = DailyProgressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, id):
        try:
            # Fetch the specific DailyProgress instance using the id from the URL
            daily_progress = Dailyprogress.objects.get(id=id)
        except Dailyprogress.DoesNotExist:
            return Response({"error": "Daily progress not found"}, status=status.HTTP_404_NOT_FOUND)

        # Partially update the instance with the provided data
        serializer = DailyProgressSerializer(daily_progress, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    # def post(self, request):
    #     # Add daily progress for the logged-in user
    #     data = request.data.copy()
    #     data["user"] = request.user.id
    #     serializer = DailyProgressSerializer(data=data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        

class LatestUpdateAPIView(APIView):
    def get(self, request, project_id=None, *args, **kwargs):
        pk = kwargs.get('pk')
        if project_id:
            
            updates = LatestUpdate.objects.filter(project_id=project_id)

            updates_serializer = LatestUpdateSerializer(updates, many=True)

            return Response({
                "updates": updates_serializer.data
            }, status=status.HTTP_200_OK)
        elif pk:
        
            try:
                update = LatestUpdate.objects.get(pk=pk)
                serializer = LatestUpdateSerializer(update)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except LatestUpdate.DoesNotExist:
                # Return an empty list instead of an error
                return Response({"updates": []}, status=status.HTTP_200_OK)
        else:
            # Fetch all projects
            updates = LatestUpdate.objects.all()
            serializer = LatestUpdateSerializer(updates, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
    def post(self, request, *args, **kwargs):
        serializer = LatestUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the new project
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, pk=None):
        try:
            update = LatestUpdate.objects.get(pk=pk)
        except LatestUpdate.DoesNotExist:
            return Response({"error": "Update not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = LatestUpdateSerializer(update, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        try:
            update = LatestUpdate.objects.get(pk=pk)
        except LatestUpdate.DoesNotExist:
            return Response({"error": "Update not found"}, status=status.HTTP_404_NOT_FOUND)
        update.delete()
        return Response({"message": "Last update deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    

class AssignedPeopleAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id=None):
        # Get the logged-in user
        logged_in_user = request.user
        
        try:
            # Fetch the logged-in user's details from RegistrationIndividual
            user_details = RegistrationIndividual.objects.get(email=logged_in_user.email)
            user_name = user_details.name
            user_role = user_details.role
        except RegistrationIndividual.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if user_role == "Intern":
            # If the user is an intern, filter projects where their name appears in assigned_to
            projects = addProject.objects.filter(assigned_to__icontains=user_name)
        else:
            # If the user is not an intern, fetch all projects
            projects = addProject.objects.all()

        # Filter by project_id if provided
        if project_id:
            try:
                project = projects.get(id=project_id)
                data = {
                    "project_id": project.id,
                    "project_name": project.project_name,
                    "assigned_to": project.assigned_to,
                    "created_at" : project.created_at,
                    "completed": project.completed,
                }
                return Response(data, status=status.HTTP_200_OK)
            except addProject.DoesNotExist:
                return Response({"You're not a part of this project, please provide the id of a valid project"}, status=status.HTTP_200_OK)

        # Return all filtered projects
        response_data = []
        for project in projects:
            data = {
                "project_id": project.id,
                "project_name": project.project_name,
                "assigned_to": project.assigned_to,
                "created_at" : project.created_at,
                "completed": project.completed,
            }
            response_data.append(data)
        return Response(response_data, status=status.HTTP_200_OK)
    
class AssignedProjectAPIView(APIView):
    def get(self, request):
        username = request.query_params.get('name')
        # Filter out projects that are marked as completed.
        projects = addProject.objects.values('assigned_to', 'id', 'project_name')
        assignments = {}
        for project in projects:
            assigned_names = [name.strip() for name in project['assigned_to'].split(',')]
            for name in assigned_names:
                if name not in assignments:
                    assignments[name] = []
                assignments[name].append({
                    "project_id": project['id'],
                    "project_name": project['project_name']
                })
        if username:
            filtered_projects = assignments.get(username, [])
            response_data = [{"assigned_to": username, "projects": filtered_projects}]
        else:
            # Build the response for all users if no username is specified.
            response_data = [{"assigned_to": name, "projects": assignments[name]} for name in assignments.keys()]
        
        return Response({"data": response_data}, status=status.HTTP_200_OK)
    

def mail(subject, body, receiver_emails):
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # Create the email message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = ""
    msg["To"] = ", ".join(receiver_emails)

    # Attach the HTML body
    html_part = MIMEText(body, "html")
    msg.attach(html_part)

    if all(email.endswith('@nokia.com') for email in receiver_emails):
        # Use Nokia Mail Relay
        server = smtplib.SMTP(settings.NOKIA_SMTP_HOST, settings.NOKIA_SMTP_PORT)
        from_email = settings.NOKIA_SENDER_EMAIL
    else:
        # Use Gmail SMTP
        server = smtplib.SMTP(settings.GMAIL_SMTP_HOST, settings.GMAIL_SMTP_PORT)
        server.starttls()
        server.login(settings.GMAIL_SENDER_EMAIL, settings.FROM_PASSWORD)
        from_email = settings.GMAIL_SENDER_EMAIL

    msg["From"] = from_email

    # Send the email
    server.sendmail(from_email, receiver_emails, msg.as_string())
    server.quit()
    
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.core.cache import cache
import random


def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def send_otp_email(email, otp):
    subject = 'Password Reset OTP'
    body = f"""
                <html>
                    <body>
                    <p>Your OTP for password reset is <strong>{otp}</strong>.</p>
                    <p>This OTP is valid for 10 minutes.</p>
                </body>
                </html>
            """
    recipient_list = [email]
    
    try:
       
        mail(subject, body, recipient_list)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def forgot_password(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            print("Form is valid")
            email = form.cleaned_data['email']
            print("Email:", email)

            try:
                print("Inside try")
                user = User.objects.get(email=email)
                # Generate OTP and store in cache
                otp = generate_otp()
                print("OTP:",otp)
                cache_key = f"password_reset_otp_{email}"
                print(cache_key)
                # Store OTP in cache for 10 minutes
                cache.set(cache_key, otp, timeout=600)  # 600 seconds = 10 minutes

                # Send OTP via email
                if send_otp_email(email, otp):
                    request.session["otp"] = otp
                    request.session.set_expiry(600)  # Expiry in 5 minutes
                    return JsonResponse({
                        'status': 'success',
                        'message': 'OTP has been sent to your email'
                    })
                else:
                    print("Failed to send email")
                    cache.delete(cache_key)
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Failed to send OTP'
                    })
            except User.DoesNotExist:
                print("User not found")
                return JsonResponse({
                    'status': 'error',
                    'message': 'No user found with this email address'
                })
        else:
            print("Form is invalid:", form.errors)
            return JsonResponse({
                'status': 'error',
                'message': str(form.errors)
            })
    else:
        form = EmailForm()
    return render(request, 'forget_password.html', {'form': form})


def verify_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        input_otp = request.POST.get("otp")

        cache_key = f"password_reset_otp_{email}"
        stored_otp = cache.get(cache_key)

        if not stored_otp:
            return JsonResponse({"status": "error", "message": "OTP expired. Request a new one."})

        if input_otp == stored_otp:
            verification_key = f"otp_verified_{email}"
            cache.set(verification_key, True, timeout=900)  # 15 minutes

            return JsonResponse({"status": "success", "message": "OTP verified. Proceed to reset password."})
        else:
            print("Invalid otp")
            return JsonResponse({"status": "error", "message": "Invalid OTP."})


def reset_password(request):
    if request.method == 'POST':

        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        
        # Check if OTP was verified
        verification_key = f"otp_verified_{email}"
        is_verified = cache.get(verification_key)

        if not is_verified:
            return JsonResponse({
                'status': 'error',
                'message': 'Verification expired. Please start over.'
            })

        try:
            # Update password
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            # Clear verification status
            cache.delete(verification_key)

            return JsonResponse({
                'status': 'success',
                'message': 'Password updated successfully'
            })

        except User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'User not found'
            })
