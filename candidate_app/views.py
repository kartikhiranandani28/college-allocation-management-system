from django.db import transaction, connection
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Candidate  # Import Candidate model
from django.contrib.auth.models import User

def is_candidate(user):
    return Candidate.objects.filter(username=user.username).exists()

def candidate_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not is_candidate(request.user):
            messages.error(request, "You must be a candidate to access this page.")
            return redirect("candidate_app:candidate_register")  # Redirect to candidate login page
        return view_func(request, *args, **kwargs)
    return _wrapped_view
def candidate_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not is_candidate(request.user):
            messages.error(request, "You must be a candidate to access this page.")
            return redirect("candidate_app:candidate_register")  # Redirect to candidate login page
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Custom decorator to ensure the user is a Candidate
@login_required(login_url='candidate_app:candidate_login')  # Redirects to login if user is anonymous
def candidate_register(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():  # Start a transaction block
                # Retrieve data from the form
                roll_no = request.POST.get('roll_no')
                username = request.user.username  # Use logged-in user's username as username or another identifier
                rank = request.POST.get('rank')
                c_name = request.POST.get('c_name')
                gender = request.POST.get('gender')
                dob = request.POST.get('dob')
                c_rank = request.POST.get('rank')  # category rank
                xii_percentage = request.POST.get('xii_percentage')
                category = request.POST.get('category')
                nationality = request.POST.get('nationality')
                address = request.POST.get('address')
                email = request.POST.get('email')
                phone = request.POST.get('phone')

                # Create and save the Candidate instance
                candidate = Candidate(
                    username=username,  # This can be username or another unique identifier
                    Roll_No=roll_no,
                    Candidate_Name=c_name,
                    Gender=gender,
                    DOB=dob,
                    Candidate_Rank=c_rank,
                    XII_Percentage=xii_percentage,
                    Category=category,
                    Nationality=nationality,
                    Address=address,
                    Email=email,
                    Phone=phone
                )
                candidate.save()  # Save candidate instance to the database

                # After saving, commit the transaction (this is implicit when the block exits without exceptions)
                messages.success(request, "Candidate registered successfully!")
                return redirect('candidate_app:candidate_home')  # Redirect to the home page after successful registration

        except Exception as e:
            # If any exception occurs, the transaction will be rolled back
            messages.error(request, f"An error occurred during registration: {e}")
            return redirect('candidate_app:candidate_register')  # Redirect back to the registration page on error

    # If not POST, render the registration form
    return render(request, 'candidate/register.html')

# Candidate login view
def candidate_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("candidate_app:candidate_home")
          
        #  if Candidate.objects.filter(username=user.username).exists():
        # #     messages.success(request, "Login successful!")  # Add success message
          
        #  else:
        # #    messages.error(request, "User  is not registered as a Candidate.")
        #    return redirect("candidate_app:candidate_login")

        else:
         messages.error(request, 'Invalid credentials')  # Set error message for invalid credentials
         return render(request, 'candidate/signup.html')  # Render login page again if login fails

    return render(request, 'candidate/login.html')  # Render login page for GET request

# Candidate signup view
def candidate_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            # Create the User instance
            user = User.objects.create_user(username=username, password=password)
            user.save()

            messages.success(request, "Candidate registered successfully!")
            return redirect('candidate_app:candidate_login')  # Redirect to login page after registration
            
        else:
            messages.error(request, "Passwords do not match.")

    return render(request, 'candidate/signup.html')

# Candidate home view
@login_required(login_url='candidate_app:candidate_login')
def candidate_home(request):
    return render(request, 'candidate/candidate_home.html')

# Logout view
def candidate_logout(request):
    logout(request)
    return redirect("cm_app:home")

# Add preference view for candidates
@login_required(login_url='candidate_app:candidate_login')
def add_preference(request, college_id, course_id):
    candidate_id = request.user.username  # Assuming the User model's username is username

    with transaction.atomic():  # Start a transaction block
        try:
            # Check if the college_id and course_id combination already exists for the candidate
            with connection.cursor() as cursor:
                cursor.execute(""" 
                    SELECT COUNT(*)
                    FROM Preference p
                    JOIN can_pref cp ON cp.Choice_ID = p.Choice_ID
                    WHERE cp.username = %s AND p.College_ID = %s AND p.Course_ID = %s
                """, [candidate_id, college_id, course_id])
                existing_count = cursor.fetchone()[0]

                # If the combination already exists, skip the insertion
                if existing_count > 0:
                    print("This preference already exists.")
                    return redirect('candidate_app:college_course_view')

                # Find the highest Choice_No for the current candidate
                cursor.execute(""" 
                    SELECT MAX(p.Choice_No) 
                    FROM can_pref cp
                    JOIN Preference p ON cp.Choice_ID = p.Choice_ID
                    WHERE cp.username = %s
                """, [candidate_id])
                max_choice_no = cursor.fetchone()[0] or 0  # If None, start from 0

                # Increment Choice_No for the new entry
                new_choice_no = max_choice_no + 1

                # Insert into Preference table with the new Choice_No
                cursor.execute(
                    "INSERT INTO Preference (College_ID, Course_ID, Choice_No) VALUES (%s, %s, %s)",
                    [college_id, course_id, new_choice_no]
                )
                choice_id = cursor.lastrowid  # Get the last inserted row's ID

                # Insert into can_pref table
                cursor.execute("INSERT INTO can_pref (username, Choice_ID) VALUES (%s, %s)", 
                               [candidate_id, choice_id])

            print("Preference added successfully with Choice No:", new_choice_no)

        except Exception as e:
            print("Error adding preference:", e)
            raise  # Re-raise the exception to trigger the rollback

    return redirect('candidate_app:college_course_view')

# Remove preference view for candidates
@login_required(login_url='candidate_app:candidate_login')
def remove_preference(request, college_id, course_id):
    candidate_id = request.user.username  # Assuming the User model's username is username

    with transaction.atomic():  # Start a transaction block
        try:
            with connection.cursor() as cursor:
                # Delete the corresponding record in `Preference` and `can_pref` table
                cursor.execute(""" 
                    DELETE cp, p
                    FROM can_pref cp
                    JOIN Preference p ON cp.Choice_ID = p.Choice_ID
                    WHERE cp.username = %s AND p.College_ID = %s AND p.Course_ID = %s
                """, [candidate_id, college_id, course_id])

            print("Preference removed successfully")
        
        except Exception as e:
            print("Error removing preference:", e)
            raise  # Re-raise the exception to trigger the rollback

    return redirect('candidate_app:college_course_view')

# View for college courses list
@login_required(login_url='candidate_app:candidate_login')
def college_course_view(request):
    candidate_id = request.user.username  # Assuming the User model's username is username

    # Query for all available college courses
    query = '''
        SELECT c.College_Name AS college_name, co.Branch_Name AS course_name, c.College_ID AS college_id, co.Course_ID AS course_id
        FROM College c
        JOIN College_Course cc ON c.College_ID = cc.College_ID
        JOIN Course co ON cc.Course_ID = co.Course_ID;
    '''

    # Query for candidate's preferences
    query1 = '''
        SELECT c.College_ID, c.College_Name, co.Course_ID, co.Branch_Name AS course_name, p.Choice_No
        FROM College c
        JOIN College_Course cc ON c.College_ID = cc.College_ID
        JOIN Course co ON cc.Course_ID = co.Course_ID
        JOIN Preference p ON p.College_ID = c.College_ID AND p.Course_ID = co.Course_ID
        JOIN can_pref cp ON cp.Choice_ID = p.Choice_ID
        WHERE cp.username = %s
        ORDER BY p.Choice_No;
    '''

    with connection.cursor() as cursor:
        cursor.execute(query)
        college_courses = cursor.fetchall()
        cursor.execute(query1, [candidate_id])
        preferences = cursor.fetchall()

    return render(request, 'candidate/college_course_list.html', {
        'college_courses': college_courses,
        'preferences': preferences
    })


from django.shortcuts import render
from django.db import connection
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import connection

@login_required(login_url='candidate_app:candidate_login')
def get_candidate_allocation(request):
    # Initialize context for the template
    context = {
        'allocation_status': None,
        'candidate_name': None,
        'allocation': None,
    }

    # Define the SQL query with a placeholder
    sql_query = """
    SELECT 
        c.Candidate_Name,
        c.Roll_No,
        p.Choice_No,
        cl.College_Name,
        co.Branch_Name,
        co.Program_Name
    FROM 
        Can_Alloc ca
    JOIN 
        Allocation a ON ca.Allocation_ID = a.Allocation_ID
    JOIN 
        Preference p ON a.Allocation_ID = p.Choice_ID
    JOIN 
        College_Course cc ON p.College_ID = cc.College_ID AND p.Course_ID = cc.Course_ID
    JOIN 
        Course co ON cc.Course_ID = co.Course_ID
    JOIN 
        Candidate c ON ca.username = c.username
    JOIN 
        College cl ON cc.College_ID = cl.College_ID  -- Join College table
    WHERE 
        ca.username = %s;  -- Use a placeholder for the username
    """

    # Use a cursor to execute the SQL query
    with connection.cursor() as cursor:
        cursor.execute(sql_query, [request.user.username])  # Pass the logged-in user's username
        result = cursor.fetchall()  # Fetch all results

        # Process the results
        if result:
            # Assuming there's only one result for a given username
            candidate_name, roll_no,choice_no, college_name, branch_name, program_name = result[0]
            context['candidate_name'] = candidate_name
            context['allocation'] = {
                'choice_no': choice_no,
                'roll_no': roll_no,
                'college_name': college_name,
                'branch_name': branch_name,
                'program_name': program_name,
            }
            context['allocation_status'] = 'Your allocation is successful!'
        else:
            context['allocation_status'] = 'No allocation found for the given username.'

    # Render the template with the context
    return render(request, 'candidate/result.html', context)

# @login_required(login_url='candidate_app:candidate_login')
# def allocation_result(request):
#     candidate_id = request.user.username

#     query1 = '''
#         SELECT 
#         FROM College c
#         JOIN College_Course cc ON c.College_ID = cc.College_ID
#         JOIN Course co ON cc.Course_ID = co.Course_ID
#         JOIN Preference p ON p.College_ID = c.College_ID AND p.Course_ID = co.Course_ID
#         JOIN can_pref cp ON cp.Choice_ID = p.Choice_ID
#         WHERE cp.username = %s
#         ORDER BY p.Choice_No;
#     '''

# # Add preference view for candidates
# @login_required(login_url='candidate_app:candidate_login')
# def add_preference(request, college_id, course_id):
#     candidate_id = request.user.username  # Assuming the User model's username is username

#     with transaction.atomic():  # Start a transaction block
#         try:
#             # Check if the college_id and course_id combination already exists for the candidate
#             with connection.cursor() as cursor:
#                 cursor.execute(""" 
#                     SELECT COUNT(*)
#                     FROM Preference p
#                     JOIN can_pref cp ON cp.Choice_ID = p.Choice_ID
#                     WHERE cp.username = %s AND p.College_ID = %s AND p.Course_ID = %s
#                 """, [candidate_id, college_id, course_id])
#                 existing_count = cursor.fetchone()[0]

#                 # If the combination already exists, skip the insertion
#                 if existing_count > 0:
#                     print("This preference already exists.")
#                     return redirect('candidate_app:college_course_view')

#                 # Find the highest choice_no for the current candidate
#                 cursor.execute(""" 
#                     SELECT MAX(p.Choice_No) 
#                     FROM can_pref cp
#                     JOIN preference p ON cp.Choice_ID = p.Choice_ID
#                     WHERE cp.username = %s
#                 """, [candidate_id])
#                 max_choice_no = cursor.fetchone()[0] or 0  # If None, start from 0

#                 # Increment choice_no for the new entry
#                 new_choice_no = max_choice_no + 1

#                 # Insert into preference table with the new choice_no
#                 cursor.execute(
#                     "INSERT INTO preference (College_ID, Course_ID, Choice_No) VALUES (%s, %s, %s)",
#                     [college_id, course_id, new_choice_no]
#                 )
#                 choice_id = cursor.lastrowid  # Get the last inserted row's ID

#                 # Insert into can_pref table
#                 cursor.execute("INSERT INTO can_pref (username, Choice_ID) VALUES (%s, %s)", 
#                                [candidate_id, choice_id])

#             print("Preference added successfully with Choice No:", new_choice_no)

#         except Exception as e:
#             print("Error adding preference:", e)
#             raise  # Re-raise the exception to trigger the rollback

#     return redirect('candidate_app:college_course_view')

# # Remove preference view for candidates
# @login_required(login_url='candidate_app:candidate_login')
# def remove_preference(request, college_id, course_id):
#     candidate_id = request.user.username  # Assuming the User model's username is username

#     with transaction.atomic():  # Start a transaction block
#         try:
#             with connection.cursor() as cursor:
#                 # Delete the corresponding record in `preference` and `can_pref` table
#                 cursor.execute(""" 
#                     DELETE cp, p
#                     FROM can_pref cp
#                     JOIN preference p ON cp.Choice_ID = p.Choice_ID
#                     WHERE cp.username = %s AND p.College_ID = %s AND p.Course_ID = %s
#                 """, [candidate_id, college_id, course_id])

#             print("Preference removed successfully")
        
#         except Exception as e:
#             print("Error removing preference:", e)
#             raise  # Re-raise the exception to trigger the rollback

#     return redirect('candidate_app:college_course_view')

# # View for college courses list
# @login_required(login_url='candidate_app:candidate_login')
# def college_course_view(request):
#     candidate_id = request.user.username  # Assuming the User model's username is username

#     # Query for all available college courses
#     query = '''
#         SELECT c.college_name AS college_name, co.branch_name AS course_name, c.college_id AS college_id, co.course_id AS course_id
#         FROM college c
#         JOIN college_course cc ON c.college_id = cc.college_id
#         JOIN course co ON cc.course_id = co.course_id;
#     '''

#     # Query for candidate's preferences
#     query1 = '''
#         SELECT c.college_id, c.college_name, co.course_id, co.branch_name AS course_name, p.choice_no
#         FROM college c
#         JOIN college_course cc ON c.college_id = cc.college_id
#         JOIN course co ON cc.course_id = co.course_id
#         JOIN preference p ON p.college_id = c.college_id AND p.course_id = co.course_id
#         JOIN can_pref cp ON cp.choice_id = p.choice_id
#         WHERE cp.username = %s
#         ORDER BY p.choice_no;
#     '''

#     with connection.cursor() as cursor:
#         cursor.execute(query)
#         college_courses = cursor.fetchall()
#         cursor.execute(query1, [candidate_id])
#         preferences = cursor.fetchall()

#     return render(request, 'candidate/college_course_list.html', {
#         'college_courses': college_courses,
#         'preferences': preferences
#     })

# # Add preference view for candidates
# @candidate_required
# @login_required(login_url='candidate_app:candidate_login')
# def add_preference(request, college_id, course_id):
#     username = request.user.username  # Assuming user model has a username field

#     with transaction.atomic():  # Start a transaction block
#         try:
#             # Check if the college_id and course_id combination already exists for the candidate
#             with connection.cursor() as cursor:
#                 cursor.execute(""" 
#                     SELECT COUNT(*)
#                     FROM preference p
#                     JOIN can_pref cp ON cp.choice_id = p.choice_id
#                     WHERE cp.username = %s AND p.college_id = %s AND p.course_id = %s
#                 """, [username, college_id, course_id])
#                 existing_count = cursor.fetchone()[0]

#                 # If the combination already exists, skip the insertion
#                 if existing_count > 0:
#                     print("This preference already exists.")
#                     return redirect('list')  # Redirect back to college courses page

#                 # Find the highest choice_no for the current candidate
#                 cursor.execute(""" 
#                     SELECT MAX(p.choice_no) 
#                     FROM can_pref cp
#                     JOIN preference p ON cp.Choice_id = p.choice_id
#                     WHERE cp.username = %s
#                 """, [username])
#                 max_choice_no = cursor.fetchone()[0] or 0  # If None, start from 0

#                 # Increment choice_no for the new entry
#                 new_choice_no = max_choice_no + 1

#                 # Insert into preference table with the new choice_no
#                 cursor.execute(
#                     "INSERT INTO preference (college_id, course_id, choice_no) VALUES (%s, %s, %s)",
#                     [college_id, course_id, new_choice_no]
#                 )
#                 choice_id = cursor.lastrowid  # Get the last inserted row's ID

#                 # Insert into can_pref table
#                 cursor.execute("INSERT INTO can_pref (username, Choice_id) VALUES (%s, %s)", 
#                                [username, choice_id])

#             print("Preference added successfully with Choice No:", new_choice_no)

#         except Exception as e:
#             # If any exception occurs, the transaction will be rolled back
#             print("Error adding preference:", e)  # Log the error for debugging
#             raise  # Re-raise the exception to trigger the rollback

#     return redirect('candidate_app:list')

# # Remove preference view for candidates
# @candidate_required
# @login_required(login_url='candidate_app:candidate_login')
# def remove_preference(request, college_id, course_id):
#     username = request.user.username

#     with transaction.atomic():  # Start a transaction block
#         try:
#             with connection.cursor() as cursor:
#                 # Delete from preference table
#                 cursor.execute("DELETE FROM preference WHERE college_id = %s AND course_id = %s", [college_id, course_id])
            
#             print("Preference removed successfully")
        
#         except Exception as e:
#             # If any exception occurs, the transaction will be rolled back
#             print("Error removing preference:", e)  # Log the error for debugging
#             raise  # Re-raise the exception to trigger the rollback

#     return redirect('list')

# # View for college courses list
# @candidate_required
# @login_required(login_url='candidate_app:candidate_login')
# def college_course_view(request):
#     # SQL query to fetch all college-course relationships
#     username = request.user.username
#     query = '''
#         SELECT c.college_name AS college_name, co.branch_name AS course_name, c.college_id AS college_id, co.course_id AS course_id
#         FROM college c
#         JOIN college_course cc ON c.college_id = cc.college_id
#         JOIN course co ON cc.course_id = co.course_id;
#     '''
#     query1 = '''
#         SELECT c.college_id, c.college_name, co.course_id, co.branch_name AS course_name, p.choice_no
#         FROM college AS c
#         JOIN college_course AS cc ON c.college_id = cc.college_id
#         JOIN course AS co ON cc.course_id = co.course_id
#         JOIN preference AS p ON p.college_id = c.college_id AND p.course_id = co.course_id
#         JOIN can_pref AS cp ON cp.choice_id = p.choice_id
#         WHERE cp.username = %s
#         ORDER BY p.choice_no;
#     '''
#     # Execute the query
#     with connection.cursor() as cursor:
#         cursor.execute(query)
#         college_courses = cursor.fetchall()
#         cursor.execute(query1, [username])
#         preferences = cursor.fetchall()

#     # Pass the results to the template
#     return render(request, 'candidates/college_course_list.html', {
#         'college_courses': college_courses,
#         'preferences': preferences
#     })

# # About page view
# def about(request):
#     return render(request, 'common/about.html')


