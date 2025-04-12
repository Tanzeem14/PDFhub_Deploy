from django.shortcuts import render, redirect
import re
import PyPDF2
import jwt # Import JWT library
from django.conf import settings # Import settings from Django
from django.http import HttpResponse, JsonResponse # Import HttpResponse and JsonResponse from Django
from django.contrib import messages
import logging
import bcrypt
import datetime
from pdfapp.db import db
from pdfapp.utils.merge import merge_pdfs # Import the merge_pdfs function from utils.py
import PyPDF2
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import render
logger = logging.getLogger(__name__)
register_table=db.register
from django.views.decorators.http import require_POST 


def generate_jwt(user):
    payload={
        'email':user['email'],
        "firstname":user['firstname'],
        'exp':datetime.datetime.now(datetime.UTC)+datetime.timedelta(days=1), # Token expires in 1 day
        'iat':datetime.datetime.now(datetime.UTC), # Time token was issued
    }
    token=jwt.encode(payload,settings.SECRET_KEY,algorithm='HS256')
    return token

from django.contrib import messages  # Ensure this is imported

def register(request):
    if request.method == "POST":
        firstname = request.POST['firstname'].strip()
        lastname = request.POST['lastname'].strip()
        email = request.POST['email'].strip()
        number = request.POST['phoneno'].strip()
        password = request.POST['password'].strip()
        con_pass = request.POST['con_pass'].strip()

        # Define regex patterns
        phone_pattern = re.compile(r'^[0-9]{10}$')
        password_pattern = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$")
        email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

        if not firstname or not lastname:
            messages.error(request, "First and Last name are required")
            return redirect("register")
        if not email_pattern.match(email):
            messages.error(request, "Invalid email address")
            return redirect("register")
        if not phone_pattern.match(number):
            messages.error(request, "Invalid phone number")
            return redirect("register")
        if len(password) < 8 or not password_pattern.match(password):
            messages.error(request, "Password must be at least 8 characters long and must contain at least one letter, one number, and one special character")
            return redirect("register")
        if password != con_pass:
            messages.error(request, "Password and Confirm Password must be the same")
            return redirect("register")

        existing_user = register_table.find_one({"email": email})
        if existing_user:
            messages.error(request, "User with this email already exists")
            return redirect("register")

        # If all validations pass, proceed with registration
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = {
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "phone_no": number,
            "password": hashed_password,
            "created_at": datetime.datetime.now(datetime.UTC),
            "updated_at": datetime.datetime.now(datetime.UTC),
        }
        try:
            register_table.insert_one(user)
            messages.success(request, "Registration Successful!")
            return redirect("login")
        except Exception as e:
            logger.error(f"Error saving user: {e}", exc_info=True)
            messages.error(request, "An error occurred while saving the user. Please try again.")
            return redirect("register")

    return render(request, "signup.html")

def login(request):
    if request.method == "POST":
        email = request.POST['email'].strip()
        password = request.POST['password'].strip()

        user = register_table.find_one({"email": email})
        if not user:
            messages.error(request, "User does not exist")
            return redirect("login")

        if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
            messages.error(request, "Invalid password")
            return redirect("login")

        token = generate_jwt(user)
        response = redirect("dashboard")
        response.set_cookie("jwt_token", token, httponly=True, max_age=3600)  # Set cookie to expire in 1 hour
        messages.success(request, "Login successful!")
        return response

    return render(request, "signin.html")

def logout(request):
    pass

def dashboard(request):
    token = request.COOKIES.get("jwt_token")
    if not token:
        return redirect("login")  # or show some error

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    
    except jwt.ExpiredSignatureError:
        messages.error(request, "Session expired. Please log in again.")
        return redirect("login")
    except jwt.InvalidTokenError:
        messages.error(request, "Invalid token. Please log in again.")
        return redirect("login")
    return render(request, "dashboard.html")
def navbar (request):
    return render(request,'navbar.html')

def compress(request):
    return render(request,'compress.html')

def convert(request):
    return render(request,'convert.html')

def merge(request):
    # Clear messages unrelated to merge
    storage = messages.get_messages(request)
    storage.used = True  # This marks all messages as used so they don't show
    if request.method == "POST":
        uploaded_files = request.FILES.getlist("pdf_files")

        if len(uploaded_files) < 2:
            messages.error(request, "Please upload at least 2 PDFs to merge.")
            return redirect("merge")

        merger = PyPDF2.PdfMerger()
        temp_files = []

        try:
            for file in uploaded_files:
                file_path = default_storage.save(f"temp/{file.name}", ContentFile(file.read()))
                temp_files.append(file_path)

                with default_storage.open(file_path, "rb") as pdf_file:
                    merger.append(pdf_file)

            merged_pdf_path = os.path.join(settings.MEDIA_ROOT, "merged_output.pdf")

            with open(merged_pdf_path, "wb") as output_file:
                merger.write(output_file)

            merger.close()

            messages.success(request, "PDFs Merged Successfully!")
            return redirect("merge")

        finally:
            for file in temp_files:
                default_storage.delete(file)

    return render(request, "merge.html")

def edit(request):
    return render(request,'edit.html')

def ai(request):
    pass

@require_POST
def logout(request):
    response = redirect("login")  # or your home page
    response.delete_cookie("jwt_token")
    messages.success(request, "You have been logged out successfully.")
    return response