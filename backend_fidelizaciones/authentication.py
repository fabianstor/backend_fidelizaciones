from firebase_admin import auth
from django.http import JsonResponse
from rest_framework.exceptions import AuthenticationFailed
from firebase_admin.auth import ExpiredIdTokenError
from django.utils.deprecation import MiddlewareMixin
from firebase_admin import auth


class CustomAuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        id_token = request.headers.get('Authorization')
        excluded_paths = [
            '/api/firebase-login/',
            '/api/restaurants/',
            '/api/users/create/'
        ]
        if request.path in excluded_paths:
            return None

        if not id_token:
            return JsonResponse({'error': 'Authorization token required'}, status=400)

        try:
            id_token = id_token.split(' ')[1]
            auth.verify_id_token(id_token)
            return None

        except ExpiredIdTokenError:
            return JsonResponse({'error': 'Token expired'}, status=401)

        except Exception as e:
            raise AuthenticationFailed(f'Authentication failed: {str(e)}')
