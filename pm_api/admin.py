from django.contrib import admin
from .models import addProject

# Register your models here.
from django.contrib import admin
from .models import addProject,RegistrationTeam,RegistrationIndividual,Feedback,LatestUpdate,Dailyprogress,Comment, Version

class AddProjectAdmin(admin.ModelAdmin):
    list_display = (
        'project_name',
        'get_description',  
        'priority',
        'led_by',
        'review',
        'research_deadline',
        'research_effort',
        'design_deadline',
        'design_effort',
        'development_deadline',
        'development_effort',
        'testing_deadline',
        'testing_effort',
        'assigned_by',
        'assigned_to',
        'current_milestone',
        'release_date',
    )

    
    def get_description(self, obj):
        return obj.description  

    get_description.short_description = 'Description' 

admin.site.register(addProject, AddProjectAdmin)

"""class BugAdmin(admin.ModelAdmin):
    list_display = ( 'bug_description','project', 'is_resolved', 'posting_time','posted_by')
    list_filter = ('project', 'is_resolved')  # Allow filtering by project name

admin.site.register(Bug, BugAdmin)"""

class VersionAdmin(admin.ModelAdmin):
    list_display = ('version_number','description')
    fields = ('version_number','description')
admin.site.register(Version,VersionAdmin)

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('feedback_description','project','posted_by','posting_time')  
    list_filter = ('feedback_description', 'project')
    
admin.site.register(Feedback, FeedbackAdmin)

class RegistrationIndividualAdmin(admin.ModelAdmin):
    list_display = ('name','email','team','role','linkedin_profile')
    list_filter = ('team','role') 
    exclude = ('password',)  

admin.site.register(RegistrationIndividual, RegistrationIndividualAdmin)

class RegistrationTeamAdmin(admin.ModelAdmin):
    list_display = ('team_name','team_manager','team_location','team_description')
    list_filter = ('team_name','team_manager')  

admin.site.register(RegistrationTeam, RegistrationTeamAdmin)

class DailyprogressAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'project', 'date', 'progress', 'isHoliday')
    
admin.site.register(Dailyprogress,DailyprogressAdmin)

class LatestUpdateAdmin(admin.ModelAdmin):
    list_display = ('user','latest_update','posted_by','posting_time')  

admin.site.register(LatestUpdate, LatestUpdateAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display =('feedback','content','posted_by','posting_time')
admin.site.register(Comment,CommentAdmin)

