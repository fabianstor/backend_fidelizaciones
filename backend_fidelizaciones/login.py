import requests
from firebase_config import db
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from google.cloud import firestore



def clean_firestore_data(data):
    cleaned = {}
    for key, value in data.items():
        if isinstance(value, firestore.DocumentReference):
            cleaned[key] = value.id
        else:
            cleaned[key] = value
    return cleaned


class FirebaseLoginView(APIView):

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Llamada a Firebase para autenticar al usuario
        firebase_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyCG4JleVMAVh7JJLSRHQmD7Oh_i5BN211E"

        # Datos que Firebase espera
        data = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }

        try:
            response = requests.post(firebase_url, data=data)
            response_data = response.json()
            if response.status_code != 200:
                return Response({"error": "Authentication failed", "details": response_data.get('error', {}).get('message')}, status=status.HTTP_400_BAD_REQUEST)
            id_token = response_data.get('idToken')
            refresh_token = response_data.get('refreshToken')
            user_query = db.collection("users").where("email", "==", email).stream()
            user_doc = next(user_query, None)
            if not user_doc:
                return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
            user_data = user_doc.to_dict()
            user_id = user_doc.id
            user_ref = db.collection("users").document(user_id)
            restaurant_query = db.collection("restaurants").where("user", "==", user_ref).limit(1).stream()
            restaurant_id = None
            for doc in restaurant_query:
                restaurant_id = doc.id
                break
            restaurant_doc = db.collection("restaurants").document(restaurant_id).get()
            restaurant_data = clean_firestore_data(restaurant_doc.to_dict()) if restaurant_id else None
            user_points_ref = db.collection("user_points").where("user_id", "==", user_id).get()
            user_data["points"] = 0
            if user_points_ref:
                points_doc = user_points_ref[0]
                user_data["points"] = points_doc.to_dict().get("points", 0)
            return Response({
                "id": user_id,
                "name": user_data.get("name"),
                "points": user_data.get("points", 0),
                "document_type": user_data.get("document_type"),
                "document_number": user_data.get("document_number"),
                "phone_number": user_data.get("phone_number"),
                "email": user_data.get("email"),
                "role": user_data.get("role"),
                "favorites": user_data.get("favorites"),
                "id_token": id_token,
                "restaurant_id": restaurant_id,
                "restaurant_data": restaurant_data,
                "tokens": 10,
                "refresh_token": refresh_token
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Authentication failed", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

