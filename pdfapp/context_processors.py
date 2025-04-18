import jwt
from django.conf import settings
from django.contrib import messages
from venv import logger
from django.http import HttpResponse, JsonResponse

def jwt_user(request):
    context = {}
    token = request.COOKIES.get("jwt_token")
    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            context['jwt_user'] = {
                'email': payload['email'],
                'firstname': payload['firstname']
            }
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            response = HttpResponse()
            response.delete_cookie("jwt_token")
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            response = HttpResponse()
            response.delete_cookie("jwt_token")
    return context
