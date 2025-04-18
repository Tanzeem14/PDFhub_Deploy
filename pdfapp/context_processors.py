import jwt
from django.conf import settings
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

def jwt_user(request):
    """
    Context processor to decode JWT token and provide user details to templates.
    """
    context = {}
    token = request.COOKIES.get("jwt_token")
    if token:
        try:
            # Decode the JWT token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            context['jwt_user'] = {
                'email': payload.get('email'),
                'firstname': payload.get('firstname'),
                'lastname': payload.get('lastname', ''),  # Default to empty string if not provided
            }
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
    return context