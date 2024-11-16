"""
URL configuration for College_Mantra project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from cm_app import views as cm_views  # Adjust this import if the home view belongs to cm_app

urlpatterns = [
    path('admin/', admin.site.urls),

    # Main homepage route handled by cm_app
    path('', include('cm_app.urls')),

    # Candidate-related URLs
    path('candidate/', include(('candidate_app.urls', 'candidate_app'), namespace='candidate_app')),

    # College-related URLs
    path('college/', include(('college_app.urls', 'college_app'), namespace='college_app')),

    # Home route (if defined in cm_app)
    path('', cm_views.home, name='home'),  # This is redundant if already included in cm_app.urls
]

