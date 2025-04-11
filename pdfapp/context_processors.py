from pdfapp.db import db
import jwt
from django.conf import settings

register_table = db.register

def user_context(request):
    token = request.COOKIES.get("jwt_token")
    if not token:
        return {}

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = register_table.find_one({'email': payload['email']}, {'_id': 0, 'firstname': 1, 'lastname': 1, 'email': 1})
        if user:
            return {'user': user}
    except jwt.ExpiredSignatureError:
        return {}
    except jwt.InvalidTokenError:
        return {}

    return {}
