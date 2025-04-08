from rest_framework import serializers
from .models import addProject, RegistrationIndividual, RegistrationTeam, Dailyprogress, Bug, Feedback, Comment, LatestUpdate, Version
from datetime import date, datetime
from django.db.models import Count

class VersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields = ['id','version_number', 'description']

class AddProjectSerializer(serializers.ModelSerializer):
    research_deadline = serializers.DateField(format='%d/%m/%Y', input_formats=['%d/%m/%Y', '%Y-%m-%d'])
    design_deadline = serializers.DateField(format='%d/%m/%Y', input_formats=['%d/%m/%Y', '%Y-%m-%d'])
    development_deadline = serializers.DateField(format='%d/%m/%Y', input_formats=['%d/%m/%Y', '%Y-%m-%d'])
    testing_deadline = serializers.DateField(format='%d/%m/%Y', input_formats=['%d/%m/%Y', '%Y-%m-%d'])
    release_date = serializers.DateField(format='%d/%m/%Y', input_formats=['%d/%m/%Y', '%Y-%m-%d'])

    total_feedback_count = serializers.SerializerMethodField()
    is_added_feedback_count = serializers.SerializerMethodField()
    open_feedback_by_person = serializers.SerializerMethodField()

    class Meta:
        model = addProject
        fields = '__all__'
        extra_fields = ['total_feedback_count', 'is_added_feedback_count', 'open_feedback_by_person']

    def get_total_feedback_count(self, obj):
        return obj.project_feedback.count()

    def get_is_added_feedback_count(self, obj):
        return obj.project_feedback.filter(is_added=True).count()

    def get_open_feedback_by_person(self, obj):
        # Get all open feedbacks
        open_feedbacks = obj.project_feedback.filter(
            is_added=False
        ).exclude(
            assigned_to__isnull=True
        ).exclude(
            assigned_to=""
        )

        # Initialize a dictionary to store counts
        person_counts = {}

        # Iterate through feedbacks and split assigned_to names
        for feedback in open_feedbacks:
            if feedback.assigned_to:
                # Split names and strip whitespace
                assigned_people = [name.strip() for name in feedback.assigned_to.split(',')]

                # Add count for each person
                for person in assigned_people:
                    if person:  # Ensure name is not empty
                        person_counts[person] = person_counts.get(person, 0) + 1

        # Convert dictionary to list of dictionaries with user and count keys
        return [{"user": user, "count": count} for user, count in person_counts.items()]
   
        
class BugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bug
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True, source='feedback_comments')

    class Meta:
        model = Feedback
        fields = '__all__'

class RegistrationIndividualSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = RegistrationIndividual
        fields = ['id', 'name', 'email', 'team', 'role', 'linkedin_profile', 'password', 'image_url']

class RegistrationTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationTeam
        fields = '__all__'

class DailyProgressSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)

    class Meta:
        model = Dailyprogress
        fields = '__all__'

class LatestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LatestUpdate
        fields = '__all__'

class AssignedPeopleSerializer(serializers.Serializer):
    project_name = serializers.CharField()
    assigned_to = serializers.ListField()
    completed = serializers.BooleanField()
