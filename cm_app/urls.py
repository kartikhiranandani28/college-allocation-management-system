
# from django.urls import path
# from . import views
# app_name = 'cm_app'
# urlpatterns = [
#     # Home route (if defined in cm_app)
#     path('', views.home, name='home'),  # This is redundant if already included in cm_app.urls
#     path('about/', views.about, name='about'),
#     path('contact/', views.contact, name='contact'),
#     path('register/', views.option, name='register'),
#     path('seat_matrix/', views.seat_matrix, name='about'),

# ]
from django.urls import path
from . import views

app_name = 'cm_app'  # This sets the namespace for your app

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('important-dates/', views.important_dates, name='important_dates'),
    path('seat_matrix/', views.seat_matrix, name='seat_matrix'),
    path('announcements/', views.announcements, name='announcements'),
    path('register/', views.option, name='register'),  # Named 'register'
    path('contact/', views.contact, name='contact'),
]