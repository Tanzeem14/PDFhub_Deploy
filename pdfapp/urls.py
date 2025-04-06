from django.urls import path
# Import the 'path' function from Django's 'urls' module. This function is used to define URL patterns.

from . import views
# Import the 'views' module from the current package. This allows you to reference view functions defined in 'views.py'.

# import views importing from top pkg
# This is a comment indicating that you could use an absolute import instead, but it's commented out.

from django.shortcuts import redirect
# Import the 'redirect' function from Django's 'shortcuts' module. This function is used to redirect users to a different URL.

from .views import register
# Import the 'register' view function from the 'views' module in the current package.
# Import the 'update_appointment_status' view function directly from the 'views' module in the current package.

from django.views.generic import TemplateView
# Import the 'TemplateView' class from Django's 'views.generic' module. This class-based view renders a template.

urlpatterns=[
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    # path('',views.dashboard,name='dashboard'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('navbar/',views.navbar,name='navbar'),
    path('logout/',views.logout,name='logout'),
    path('compress/',views.compress,name='compress'),
    path('convert/',views.convert,name='convert'),
    path('merge/',views.merge,name='merge'),
    path('edit/',views.edit,name='edit'),
    path('ai/',views.ai,name='ai'),
]