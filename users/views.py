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
        name = request.data.get("name")
        favorites = request.data.get("favorites", [])
        display_name = request.data.get("display_name", "")

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = auth.create_user(
                email=email,
                password=password,
                display_name=display_name,
            )
            users = db.collection("users")
            users.add({
                "name": name,
                "role": "client",
                "favorites": favorites,
                "email": email,
            })
            return Response({
                "message": "User created successfully",
                "user_id": user.uid
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        name = request.data.get("name")
        email = request.data.get("email")
        favorites = request.data.get("favorites", [])
        display_name = request.data.get("display_name", "")

        if not name or not email:
            return Response({"error": "Name and email are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            auth.update_user(
                pk,
                email=email,
                display_name=display_name,
            )
            users = db.collection("users").document(pk)
            users.update({
                "name": name,
                "email": email,
                "favorites": favorites,
            })
            return Response({"message": "User updated successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
