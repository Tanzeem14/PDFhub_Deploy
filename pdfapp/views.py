from venv import logger
from django.shortcuts import render, redirect
import re
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
from pdfapp.utils.compress import compress_pdf  # Import the compress_pdf function
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import render
# logger = logging.getLogger(__name__)
import logging
logging.basicConfig(level=logging.WARNING)  # Or logging.ERROR to only show errors

register_table=db.register
from django.views.decorators.http import require_POST 
from pdfapp.utils.convert import convert_pdf_to_word, convert_pdf_to_images, convert_pdf_to_pptx

import zipfile



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
    """
    Handle the PDF compression request.
    """
    if request.method == "POST":
        uploaded_file = request.FILES.get("pdf_file")  # Get the uploaded file
        quality = request.POST.get("option", "/ebook")  # Get the selected quality option

        if not uploaded_file:
            messages.error(request, "Please upload a PDF file.")
            return redirect("compress")

        try:
            # Call the utility function to compress the PDF
            compressed_file_path = compress_pdf(uploaded_file, quality)
            relative_path = os.path.relpath(compressed_file_path, settings.MEDIA_ROOT)  # Get relative path for MEDIA_URL
            messages.success(request, f"PDF Compressed Successfully!")
        except Exception as e:
            messages.error(request, f"An error occurred while compressing the PDF: {str(e)}")

    return render(request, "compress.html")


from django.utils.html import format_html


def convert(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("pdf_file")
        format_option = request.POST.get("format_option")

        if not uploaded_file:
            messages.error(request, "Please upload a PDF file.")
            return redirect("convert")

        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
        converted_dir = os.path.join(settings.MEDIA_ROOT, "converted")
        os.makedirs(temp_dir, exist_ok=True)
        os.makedirs(converted_dir, exist_ok=True)

        filename = os.path.splitext(uploaded_file.name)[0]
        temp_pdf_path = os.path.join(temp_dir, uploaded_file.name)

        with open(temp_pdf_path, "wb") as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)

        try:
            if format_option == "docx":
                output_file = os.path.join(converted_dir, f"{filename}.docx")
                convert_pdf_to_word(temp_pdf_path, output_file)
                file_url = os.path.join(settings.MEDIA_URL, "converted", f"{filename}.docx")
                messages.success(request, format_html("Converted to Word! <a href='{}' download>Download Word</a>", file_url))

            elif format_option == "jpg":
                image_dir = os.path.join(converted_dir, f"{filename}_images")
                image_paths = convert_pdf_to_images(temp_pdf_path, image_dir)

                zip_path = os.path.join(converted_dir, f"{filename}.jpg.zip")
                with zipfile.ZipFile(zip_path, "w") as zf:
                    for image_path in image_paths:
                        zf.write(image_path, os.path.basename(image_path))

                file_url = os.path.join(settings.MEDIA_URL, "converted", f"{filename}.jpg.zip")
                messages.success(request, format_html("Converted to images! <a href='{}' download>Download ZIP</a>", file_url))

            elif format_option == "pptx":
                output_file = os.path.join(converted_dir, f"{filename}.pptx")
                convert_pdf_to_pptx(temp_pdf_path, output_file)
                file_url = os.path.join(settings.MEDIA_URL, "converted", f"{filename}.pptx")
                messages.success(request, format_html("Converted to PowerPoint! <a href='{}' download>Download PPTX</a>", file_url))

            else:
                messages.error(request, "Invalid format selected.")
                return redirect("convert")

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect("convert")

        finally:
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)

    return render(request, "convert.html")

def merge(request):
    storage = messages.get_messages(request)
    storage.used = True

    if request.method == "POST":
        uploaded_files = request.FILES.getlist("pdf_files")
        success, message = merge_pdfs(uploaded_files)

        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)

        return redirect("merge")

    return render(request, "merge.html")


def edit(request):
    return render(request,'edit.html')

def ai(request):
    return render(request,'ai.html')

def summarization_view(request):
    return render(request, 'summarization.html')

def translation_view(request):
    return render(request, 'translation.html')

def chat_view(request):
    return render(request, 'chat.html')

@require_POST
def logout(request):
    response = redirect("login")  # or your home page
    response.delete_cookie("jwt_token")
    messages.success(request, "You have been logged out successfully.")
    return response