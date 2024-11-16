from django.shortcuts import render
from django.db import transaction, connection
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import College  # Import College model
from django.contrib.auth.models import User

def is_college(user):
    return College.objects.filter(college_id=user.username).exists()

# Custom decorator to ensure the user is a College member
def college_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not is_college(request.user):
            messages.error(request, "You must be a college member to access this page.")
            return redirect("college_app:college_login")  # Redirect to college login page
        return view_func(request, *args, **kwargs)
    return _wrapped_view
# College login view
def college_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            # Check if the user is associated with a College
            if College.objects.filter(College_ID=user.username).exists():
                return redirect("college_app:college_home")  # Redirect after successful login
            else:
                return redirect("college_app:college_login")
        else:
            messages.error(request, 'Invalid credentials')
            return render(request, 'colleges/login.html')

    return render(request, 'colleges/login.html')  # Render login page


# College signup view
def college_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            try:
                # Create the User instance
                user = User.objects.create_user(username=username, password=password)
                user.save()

                # Additional college information can be added here if needed
                messages.success(request, "College registered successfully!")
                return redirect('college_app:college_login')  # Redirect to login page after registration
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
        else:
            messages.error(request, "Passwords do not match.")

    return render(request, 'colleges/signup.html')


# College logout view
def college_logout(request):
    logout(request)
    return redirect("college_login")


@login_required(login_url='college_app:college_login')  # Ensures the user is logged in before accessing this page
def college_register(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():  # Start a transaction block to ensure atomicity

                # Retrieve the data from the registration form
                college_id = request.user.username  # Using the username as the college_id
                college_name = request.POST.get('college_name')
                college_type = request.POST.get('college_type')
                contact_no = request.POST.get('contact_no')
                email = request.POST.get('email')
                location = request.POST.get('location')
                website = request.POST.get('website')

                # Validate required fields (you can add more validations here as needed)
                if not college_name or not college_type or not contact_no or not email:
                    raise ValueError("All fields are required!")

                # Create and save the College instance
                college = College(
                    College_ID=college_id,  # Using the logged-in user's username as the college ID
                    College_Name=college_name,
                    College_Type=college_type,
                    Contact_No=contact_no,
                    Email=email,
                    Location=location,
                    Website=website
                )
                college.save()

                # If everything goes well, show a success message
                messages.success(request, "College registered successfully!")
                return redirect('college_app:college_home')  # Redirect to the college home page after successful registration

        except Exception as e:
            # If any error occurs, the transaction will be rolled back
            messages.error(request, f"An error occurred during registration: {e}")
            return redirect('college_app:college_register')  # Redirect back to the registration page on error

    # If the method is GET, render the registration form
    return render(request, 'colleges/register.html')


# Function to fetch the college list
def get_college_list():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM College")  # Adjust table name to match your model table
        results = cursor.fetchall()
    return results


# Function to fetch the preference list
def get_preference_list():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM preference")
        results = cursor.fetchall()
    return results


# Function to fetch the course list
def get_course_list():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Course")
        results = cursor.fetchall()
    return results


# View to display college list
def college_list(request):
    # Fetch college, preference, and course lists
    colleges = get_college_list()
    preferences = get_preference_list()
    courses = get_course_list()

    return render(request, 'colleges/college_list.html', {
        'colleges': colleges,
        'preference': preferences,
        'courses': courses
    })

# Home page for colleges
def college_home(request):
    return render(request, 'colleges/home.html')
