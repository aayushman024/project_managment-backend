from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password
from django.conf import settings
from datetime import timedelta
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django.db.models.signals import pre_save
from django.dispatch import receiver
import datetime

class Version(models.Model):
    version_number = models.CharField(max_length=10)
    description = models.CharField(max_length=500)

class addProject(models.Model):
    project_name = models.CharField(max_length=500)
    created_at = models.DateField(default=datetime.date.today)
    description = models.TextField()
    priority = models.CharField(max_length=50, default='')
    led_by = models.CharField(max_length=100, default='')
    review = models.CharField(max_length=50, default="Monday")
    research_deadline = models.DateField(default=datetime.date.today)
    research_effort = models.CharField(max_length=5)
    design_deadline = models.DateField(default=datetime.date.today)
    design_effort = models.CharField(max_length=5)
    development_deadline = models.DateField(default=datetime.date.today)
    development_effort = models.CharField(max_length=5)
    testing_deadline = models.DateField(default=datetime.date.today)
    testing_effort = models.CharField(max_length=5)
    assigned_by = models.CharField(max_length=200)
    assigned_to = models.CharField(max_length=500)
    current_milestone = models.CharField(max_length=200, default='Null')
    last_update = models.DateField(default=datetime.date.today)
    completion_percentage = models.FloatField(default=0.0)
    completed = models.BooleanField(default=False)
    release_date = models.DateField()
    project_url = models.CharField(max_length=200, null=True, blank=True)
    hold_reason = models.CharField(null= True, blank= True, max_length= 500)
    onHold_till = models.DateField(null= True, blank= True)
    onHold_by = models.CharField(null= True, blank= True, max_length= 200)

    def save(self, *args, **kwargs):
        if self.pk:  
            self.last_update = now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.project_name


from django.db import models
from django.utils.timezone import now
import datetime

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey('addProject', on_delete=models.CASCADE, related_name='project_feedback')
    project_index = models.PositiveIntegerField(editable=False) 
    feedback_description = models.TextField()
    posting_time = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(blank=True, null=True)
    posted_by = models.CharField(max_length=200)
    is_added = models.BooleanField(default=False)
    assigned_to = models.CharField(max_length=200, default="", null=True, blank=True)
    is_bug = models.BooleanField(default=False)
    reported_by = models.CharField(max_length=200, null=True, blank=True)
    completion_time = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Ensure deadline is None if an empty string is provided
        if self.deadline == "":
            self.deadline = None

        # Set project_index if not already set
        if not self.project_index:
            max_index = Feedback.objects.filter(project=self.project).aggregate(models.Max('project_index'))['project_index__max']
            self.project_index = (max_index or 0) + 1

        # Set or reset completion_time based on is_feedback_closed
        if self.is_added and not self.completion_time:
            self.completion_time = now()
        elif not self.is_added:
            self.completion_time = None

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['project', 'project_index']

    def __str__(self):
        return f"Feedback #{self.project_index} by {self.posted_by} on Project {self.project.project_name}"

    def add_comment(self, content, posted_by):
        comment = Comment.objects.create(
            feedback=self,
            content=content,
            posted_by=posted_by
        )
        return comment

class Bug(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey('addProject', on_delete=models.CASCADE, related_name='project_bugs')
    bug_description = models.TextField()
    is_resolved = models.BooleanField(default=False)
    posting_time = models.DateField(auto_now_add=True)
    posted_by = models.CharField(max_length=200)


class Comment(models.Model):
    feedback = models.ForeignKey('Feedback', on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    content_id = models.AutoField(primary_key=True)
    posted_by = models.CharField(max_length=200)
    posting_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.posted_by} on Feedback {self.feedback.id}"


from django.db import models
from django.utils.timezone import now


class RegistrationIndividual(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    team = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    linkedin_profile = models.URLField(blank=True, null=True)
    password = models.CharField(max_length=255)
    image_url = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        
        with transaction.atomic():
            is_new = self.pk is None
            if not self.password.startswith('pbkdf2_sha256$'):
                self.password = make_password(self.password)

            super().save(*args, **kwargs)  

            if is_new:

                User.objects.create(
                    username=self.email,
                    first_name=self.name.split()[0] if self.name else "",
                    last_name=" ".join(self.name.split()[1:]) if len(self.name.split()) > 1 else "",
                    email=self.email,
                    password=self.password,
                )
            else:
                # Update the existing User if the RegistrationIndividual is updated
                try:
                    user = User.objects.get(username=self.email)
                    user.first_name = self.name.split()[0] if self.name else ""
                    user.last_name = " ".join(self.name.split()[1:]) if len(self.name.split()) > 1 else ""
                    user.email = self.email
                    if self.password != user.password:  
                        user.password = make_password(self.password)
                    user.save()
                except User.DoesNotExist:
                    hashed_password = make_password(self.password)
                    User.objects.create(
                        username=self.email,
                        first_name=self.name.split()[0] if self.name else "",
                        last_name=" ".join(self.name.split()[1:]) if len(self.name.split()) > 1 else "",
                        email=self.email,
                        password=hashed_password,
                    )

    def __str__(self):
        return self.name

class RegistrationTeam(models.Model):
    team_name = models.CharField(max_length=255, unique=True)
    team_manager = models.CharField(max_length=255)
    team_location = models.CharField(max_length=255)
    team_description = models.TextField()

    def __str__(self):
        return self.team_name
    
# class Dailyprogress(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='daily_progress',null=True, blank=True)  
#     date = models.DateField(default=now)
#     progress = models.TextField(default='')

class Dailyprogress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='daily_progress', null=True, blank=True)  
    project = models.ForeignKey('addProject', on_delete=models.CASCADE, related_name='daily_progress', null=True, blank=True)
    date = models.DateField(default=now)
    progress = models.TextField(default='')
    name = models.CharField(max_length=255, default='')
    isHoliday = models.BooleanField()
    
    def save(self, *args, **kwargs):
        if self.user:
            self.name = f"{self.user.first_name} {self.user.last_name}".strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Progress by {self.name} for project {self.project.project_name if self.project else 'No Project'}"


class LatestUpdate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey('addProject', on_delete=models.CASCADE, related_name='project_update')
    latest_update = models.TextField()
    posted_by = models.CharField(max_length=200)
    posting_time = models.DateTimeField(auto_now_add=True)

class AssignedPeople:
    # This model is non-database because you only need to fetch fields from addProject
    project_name: str
    assigned_to: list
    completed: bool