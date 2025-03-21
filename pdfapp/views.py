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
logger = logging.getLogger(__name__)
register_table=db.register


def generate_jwt(user):
    payload={
        'email':user['email'],
        "firstname":user['firstname'],
        'exp':datetime.datetime.now(datetime.UTC)+datetime.timedelta(days=1), # Token expires in 1 day
        'iat':datetime.datetime.now(datetime.UTC), # Time token was issued
    }
    token=jwt.encode(payload,settings.SECRET_KEY,algorithm='HS256')
    return token

def register(request):
    if request.method == "POST":
        firstname = request.POST['firstname'].strip()
        lastname = request.POST['lastname'].strip()
        email = request.POST['email'].strip()
        number = request.POST['phoneno'].strip()
        password = request.POST['password'].strip()
        con_pass = request.POST['con_pass'].strip()

        # Define regex patterns
        phone_pattern=re.compile(r'^[0-9]{10}$')
        password_pattern = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$")        
        email_pattern=re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        # email_pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')  # Validates email format

        if not firstname or not lastname:
            return render(request,"signup.html",{"message":"First and Last name are required"})
        if not email_pattern.match(email):
            return render(request, 'signup.html', {'message': 'Invalid email address'})
        if not phone_pattern.match(number):
            return render(request,'signup.html',{'message':'Invalid phone number'})
        if len(password) < 8 or not password_pattern.match(password):
            return render(request, 'signup.html', {'message': 'Password must be at least 8 characters long and must contain at least one letter and one number'})
        elif password != con_pass:
            return render(request, 'signup.html', {'message': 'Password and Confirm Password must be the same'})

        existing_user=register_table.find_one({"email":email})
        if existing_user:
            return render(request, 'signup.html', {'message': 'User with email already exists'})

        # If all validations pass, proceed with registration
        # hashed_password = make_password(password)
        hashed_password=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
        user ={
            "firstname":firstname,
            "lastname":lastname,
            "email":email,  
            "phone_no":number,
            "password":hashed_password,
            "created_at": datetime.datetime.now(datetime.UTC),
            "updated_at":datetime.datetime.now(datetime.UTC),

        }
        try:
            register_table.insert_one(user)
            # messages.success(request, "Registration Successful!")
            return redirect("login")
        except Exception as e:
            logger.error(f"Error saving user: {e}",exc_info=True)
            return render(request, 'signup.html', {'message': 'An error occurred while saving the user. Please try again.'})

    return render(request, "signup.html")


def login(request):
    if request.method=="POST":
        email=request.POST['email'].strip()
        password=request.POST['password'].strip()

        user=register_table.find_one({"email":email})
        if not user:
            return render(request,"signin.html",{"message":"User does not exist"})
       
        if not bcrypt.checkpw(password.encode('utf-8'),user['password']):
            return render(request,"signin.html",{"message":"Invalid password"})
        
        token=generate_jwt(user)
        response= redirect("dashboard")
        response.set_cookie("jwt_token",token,httponly=True,max_age=3600) # Set cookie to expire in 1 hour    
        return response
    return render(request,"signin.html")

def logout(request):
    pass

def dashboard(request):
    pass