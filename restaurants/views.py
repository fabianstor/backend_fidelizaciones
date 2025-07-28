from backend_fidelizaciones.enums import RoleEnum
from firebase_config import db
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
import random
import string
from firebase_admin import auth

def clean_firestore_data(data):
    for key, value in data.items():
        if hasattr(value, 'path'):
            data[key] = value.path
    return data


class RestaurantsView(APIView):

    def post(self, request):
        name = request.data.get("name", "")
        owner_name = request.data.get("owner_name", "")
        description = request.data.get("description", "")
        email = request.data.get("email", "")
        phone_number = request.data.get("phone_number", "")
        tags = request.data.get("tags", [])
        address = request.data.get("address", "")
        password = request.data.get("password", "")

        user = db.collection("users")

        user.add({
            "name": owner_name,
            "email": email,
            "phone_number": phone_number,
            "address": address,

            "role": RoleEnum.RESTAURANT.value,
        })
        auth.create_user(
            email=email,
            password=password,
            display_name=owner_name,
        )
        user_id = None
        user_ref = user.where("email", "==", email).stream()
        for doc in user_ref:
            user_id = doc.id
            break
        restaurant = db.collection("restaurants")
        restaurant.add({
            "name": name,
            "user": db.document(f"users/{user_id}"),
            "description": description,
            "address": address,
            "tags": tags,
            "rate": 4.5,
            "active": False
        })

        return Response({"message": "Restaurant created successfully"}, status=status.HTTP_201_CREATED)

    def get(self, request):
        restaurants = db.collection("restaurants").stream()
        response = []
        for restaurant in restaurants:
            foods = db.collection("foods").stream()
            foods_list = []
            for food in foods:
                food_dict = food.to_dict()
                clean_firestore_data(food_dict)
                food_dict["id"] = food.id
                foods_list.append(food_dict)
            restaurant_data = restaurant.to_dict()
            clean_firestore_data(restaurant_data)
            restaurant_data["foods"] = foods_list
            restaurant_data["id"] = restaurant.id
            response.append(restaurant_data)
        return Response({"message": "Restaurants list", "data": response}, status=status.HTTP_200_OK)

    def put(self, request, restaurant_id):
        name = request.data.get("name")
        image = request.data.get("image", "")
        rate = request.data.get("rate", "")
        restaurant = db.collection("restaurants").document(restaurant_id)
        restaurant.update({
            "name": name,
            "image": image,
            "rate": rate
        })
        return Response({"message": "Restaurant updated successfully"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='activate')
    def active(self, request, restaurant_id):
        restaurant = db.collection("restaurants").document(restaurant_id)
        restaurant.update({"active": True})
        return Response({"message": "Restaurant activated successfully"}, status=status.HTTP_200_OK)
