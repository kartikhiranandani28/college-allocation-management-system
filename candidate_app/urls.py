from django.urls import path
from . import views

app_name = 'candidate_app'

urlpatterns = [

    # Candidate URLs
    path('signup/', views.candidate_signup, name='candidate_signup'),
    path('login/', views.candidate_login, name='candidate_login'),
    path('logout/', views.candidate_logout, name='candidate_logout'),
    path('register/', views.candidate_register, name='candidate_register'),
    path('home/', views.candidate_home, name='candidate_home'),

    # Preference-related URLs
    path('add_preference/<int:college_id>/<int:course_id>/', views.add_preference, name='add_preference'),
    path('remove_preference/<int:college_id>/<int:course_id>/', views.remove_preference, name='remove_preference'),
    path('list/', views.college_course_view, name='college_course_view'),
    # Uncomment the following line if needed:
    # path('preferences/', views.remove, name='preferences'),

    # Uncomment the following line if needed:
    # path('allocate/', views.allocate_colleges, name='allocate'),
]
