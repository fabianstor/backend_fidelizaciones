import requests
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

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
            # Realizar la solicitud a Firebase para autenticar al usuario
            response = requests.post(firebase_url, data=data)
            response_data = response.json()

            # Si Firebase retorna un error, lanzamos una excepción
            if response.status_code != 200:
                return Response({"error": "Authentication failed", "details": response_data.get('error', {}).get('message')}, status=status.HTTP_400_BAD_REQUEST)

            # Extraer el id_token del usuario autenticado
            id_token = response_data.get('idToken')

            # Opcionalmente, también puedes obtener el refresh token si lo necesitas
            refresh_token = response_data.get('refreshToken')

            # Devolver el id_token y refresh_token como respuesta al frontend
            return Response({
                'id_token': id_token,
                'refresh_token': refresh_token
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": "Authentication failed", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

