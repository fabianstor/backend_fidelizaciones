from firebase_config import db
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

def clean_firestore_data(data):
    for key, value in data.items():
        if hasattr(value, 'path'):
            data[key] = value.path
    return data


class RestaurantsView(APIView):

    def post(self, request):
        name = request.data.get("name", "")
        image = request.data.get("image", "")
        rate = request.data.get("rate", "")
        description = request.data.get("description", "")
        address = request.data.get("address", "")
        tags = request.data.get("tags", [])

        restaurant = db.collection("restaurants")
        restaurant.add({
            "name": name,
            "address": address,
            "image": image,
            "rate": rate,
            "description": description,
            "tags": tags,
        })

        return Response({"message": "Restaurant created successfully"}, status=status.HTTP_201_CREATED)

    def get(self, request):
        restaurants = db.collection("restaurants").stream()
        response = []

        for restaurant in restaurants:
            menu_ref = db.document(f"menus/{restaurant.id}")
            foods = db.collection("foods").where("menu", "==", menu_ref).stream()

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
