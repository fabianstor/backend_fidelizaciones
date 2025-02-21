# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .firebase_config import db
from firebase_admin import auth


class CreateUserAPIView(APIView):

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        display_name = request.data.get("display_name", "")

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Crea un usuario en Firebase Authentication
            user = auth.create_user(
                email=email,
                password=password,
                display_name=display_name,
            )

            return Response({
                "message": "User created successfully",
                "user_id": user.uid
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
