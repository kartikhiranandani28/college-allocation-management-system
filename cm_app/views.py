from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection
import MySQLdb

from django.http import JsonResponse

# Create your views here.

from django.db import transaction
def home(request):
    return render(request,'colleges/common_home.html')
# About page view
def about(request):
    return render(request, 'common/about.html')
def contact(request):
    return render(request,'common/contact.html')
def option(request):
    return render(request,'common/register.html')









    