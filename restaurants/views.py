from firebase_config import db
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


class RestaurantsView(APIView):

    def post(self, request):
        name = request.data.get("name", "")
        email = request.data.get("email", "")
        image = request.data.get("image", "")
        rate = request.data.get("rate", "")
        address = request.data.get("address", "")

        restaurant = db.collection("restaurants")
        restaurant.add({
            "name": name,
            "email": email,
            "address": address,
            "image": image,
            "rate": rate
        })
        return Response({"message": "Restaurant created successfully"}, status=status.HTTP_201_CREATED)

    def get(self, request):
        restaurants = db.collection("restaurants").stream()
        response = []
        for restaurant in restaurants:
            restaurant_data = restaurant.to_dict()
            restaurant_data["id"] = restaurant.id
            response.append(restaurant_data)
        return Response(response, status=status.HTTP_200_OK)

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
