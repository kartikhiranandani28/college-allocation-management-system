
from django.urls import path
from . import views
app_name = 'college_app'
urlpatterns = [

    # College URLs
    path('signup/', views.college_signup, name='college_signup'),
    path('login/', views.college_login, name='college_login'),
    path('logout/', views.college_logout, name='college_logout'),
    path('register/', views.college_register, name='college_register'),
    path('home/', views.college_home, name='college_home'),
    path('courses/', views.college_courses, name='college_courses')
    # path('', views.home, name='common_home'),
   
]
