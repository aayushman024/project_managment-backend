from django.urls import path
from .views import AddProjectAPIView, QuickInsightsAPIView, RegistrationIndividualAPIView, LatestUpdateAPIView, RegistrationTeamAPIView, LoginAPIView, BugAPIView, FeedbackAPIView, DailyProgressAPIView, AssignedPeopleAPIView, AssignedProjectAPIView, CommentAPIView,VersionAPIView

urlpatterns = [
    path('projects/', AddProjectAPIView.as_view(), name='projects-api'), 
    path('projects/<int:pk>/', AddProjectAPIView.as_view(), name='project-detail-api'),  
    path('quick-insights/', QuickInsightsAPIView.as_view(), name='quick-insights-api'),
    path('api/bugs/', BugAPIView.as_view(), name='bug_api'),  # List and create
    path('api/bugs/<int:pk>/', BugAPIView.as_view(), name='bug_detail_api'),
    path('api/bugs/project/<int:project_id>/', BugAPIView.as_view(), name='project-bugs'),
    path('api/feedback/', FeedbackAPIView.as_view(), name='feedback_list'), 
    path('api/feedback/<int:pk>/', FeedbackAPIView.as_view(), name='feedback_detail'),
    path('api/feedback/project/<int:project_id>/', FeedbackAPIView.as_view(), name='project-feedback'),
    path('api/feedback/user/<str:username>/', FeedbackAPIView.as_view(), name='user-feedback'),
    path('api/login/', LoginAPIView.as_view(), name='login'),
    path('api/individuals/', RegistrationIndividualAPIView.as_view(), name='individuals_list'),  # xAll individuals
    path('api/individuals/<int:pk>/', RegistrationIndividualAPIView.as_view(), name='individual_detail'),
    path('api/teams/', RegistrationTeamAPIView.as_view(), name='teams_list'),  
    path('api/teams/<int:pk>/', RegistrationTeamAPIView.as_view(), name='team_detail'), 
    path('daily-progress/', DailyProgressAPIView.as_view(), name='daily-progress'),  # Logged-in user's progress
    path('daily-progress/<int:user_id>/', DailyProgressAPIView.as_view(), name='user-specific-daily-progress'),
    path('daily-progress/project/<int:project_id>/', DailyProgressAPIView.as_view(), name='daily-progress-project'),
    path('daily-progress/edit/<int:id>/', DailyProgressAPIView.as_view(), name='edit-daily-progress'),
    path('latest-update/', LatestUpdateAPIView.as_view(), name='update_list'), 
    path('latest-update/<int:pk>/', LatestUpdateAPIView.as_view(), name='update_detail'),
    path('latest-update/project/<int:project_id>/', LatestUpdateAPIView.as_view(), name='project-update'),
    path('assigned-people/', AssignedPeopleAPIView.as_view(), name='assigned_people_all'),
    path('assigned-people/<int:project_id>/', AssignedPeopleAPIView.as_view(), name='assigned_people_single'),
    path('assigned-project/', AssignedProjectAPIView.as_view(), name='assigned_project'),
    # URL for posting comments on a particular feedback
    path('api/feedback/comment/', CommentAPIView.as_view(), name='post_comment'),
    path('api/fetch-version/',VersionAPIView.as_view(),name='get_version'),
]
