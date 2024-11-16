
from django.urls import path
from . import views
app_name = 'cm_app'
urlpatterns = [
    # Home route (if defined in cm_app)
    path('', views.home, name='home'),  # This is redundant if already included in cm_app.urls
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.option, name='register'),
]
