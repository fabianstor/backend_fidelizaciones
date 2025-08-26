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
        document_type = request.data.get("document_type", "")
        document_number = request.data.get("document_number", "")
        name = request.data.get("name")
        favorites = request.data.get("favorites", [])
        display_name = request.data.get("display_name", "")

        if not email or not password:
            return Response({"error": "Correo y contraseña requeridos"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_user_document = db.collection("users").where("document_number", "==", document_number).stream()
            for doc in validate_user_document:
                return Response({"error": "Número de documento ya está registrado"}, status=status.HTTP_400_BAD_REQUEST)
            validate_user_email = db.collection("users").where("email", "==", email).stream()
            for doc in validate_user_email:
                return Response({"error": "Correo electronico ya está registrado"}, status=status.HTTP_400_BAD_REQUEST)
            user = auth.create_user(
                email=email,
                password=password,
                display_name=display_name,
            )
            validate_user_document = db.collection("users").where("document_number", "==", document_number).stream()
            for doc in validate_user_document:
                return Response({"error": "Document number already exists"}, status=status.HTTP_400_BAD_REQUEST)
            validate_user_email = db.collection("users").where("email", "==", email).stream()
            for doc in validate_user_email:
                return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            users = db.collection("users")
            users.add({
                "name": name,
                "document_type": document_type,
                "document_number": document_number,
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
        document_type = request.data.get("document_type", "")
        document_number = request.data.get("document_number", "")
        favorites = request.data.get("favorites", [])
        display_name = request.data.get("display_name", "")

        if not name or not email:
            return Response({"error": "Name and email are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_user_document = db.collection("users").where("document_number", "==", document_number).stream()
            for doc in validate_user_document:
                if doc.id != pk:
                    return Response({"error": "Document number already exists"}, status=status.HTTP_400_BAD_REQUEST)
            validate_user_email = db.collection("users").where("email", "==", email).stream()
            for doc in validate_user_email:
                if doc.id != pk:
                    return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            users = db.collection("users").document(pk)
            users.update({
                "name": name,
                "document_type": document_type,
                "document_number": document_number,
                "email": email,
                "favorites": favorites,
            })
            return Response({"message": "User updated successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ListUsersAPIView(APIView):

    def get(self, request):
        user_id = request.query_params.get("user_id", None)
        if user_id:
            user_doc = db.collection("users").document(user_id).get()
            if not user_doc.exists:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            user_data = user_doc.to_dict()
            user_points_ref = db.collection("user_points").where("user_id", "==", user_id).get()
            user_data["points"] = 0
            if user_points_ref:
                points_doc = user_points_ref[0]
                user_data["points"] = points_doc.to_dict().get("points", 0)
            user_data["id"] = user_doc.id
            return Response({"users": user_data}, status=status.HTTP_200_OK)
        users_ref = db.collection("users")
        users = users_ref.stream()
        users_list = []
        for user in users:
            user_dict = user.to_dict()
            user_points_ref = db.collection("user_points").where("user_id", "==", user.id).get()
            user_dict["points"] = 0
            if user_points_ref:
                points_doc = user_points_ref[0]
                user_dict["points"] = points_doc.to_dict().get("points", 0)
            user_dict["id"] = user.id
            users_list.append(user_dict)
        return Response({"users": users_list}, status=status.HTTP_200_OK)
