from firebase_config import db
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class MenusView(APIView):

    def post(self, request):
        name = request.data.get("name")
        description = request.data.get("description")
        restaurant_id = request.data.get("restaurant_id")
        category = request.data.get("category")
        price = request.data.get("price")
        preparation_time = request.data.get("preparation_time")
        image = request.data.get("image")

        restaurant_ref = db.collection("restaurants").document(restaurant_id)

        if not restaurant_id:
            return Response({"error": "restaurant_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        foods = db.collection("foods")

        foods.add({
            "name": name,
            "image": image,
            "category": category,
            "price": price,
            "description": description,
            "available": True,
            "state": True,
            "restaurant_id": restaurant_ref,
            "preparation_time": preparation_time
        })

        return Response({"message": "Menu created successfully"}, status=status.HTTP_201_CREATED)


    def get(self, request):
        restaurant_id = request.query_params.get("restaurant_id")
        restaurant_ref = db.collection("restaurants").document(restaurant_id)
        if not restaurant_id:
            return Response({"error": "restaurant not found"}, status=status.HTTP_404_NOT_FOUND)
        menus = db.collection("foods") \
            .where("restaurant_id", "==", restaurant_ref) \
            .where("state", "==", True) \
            .stream()
        if not menus:
            return Response({"message": "No menus found"}, status=status.HTTP_404_NOT_FOUND)
        response = []
        for menu in menus:
            menu_data = menu.to_dict()
            menu_data.pop("restaurant_id", None)
            response.append({
                "id": menu.id,
                "data": menu_data
            })
        response_data = {
            "restaurant_id": restaurant_id,
            "menu": response
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        name = request.data.get("name")
        description = request.data.get("description")
        restaurant_id = request.data.get("restaurant_id")
        category = request.data.get("category")
        price = request.data.get("price")
        preparation_time = request.data.get("preparation_time")
        image = request.data.get("image")

        if not name or not description or not restaurant_id or not category or not price:
            return Response({"message": "Todos los campos son requeridos"}, status=status.HTTP_400_BAD_REQUEST)

        foods = db.collection("foods").document(pk)
        restaurant_ref = db.collection("restaurants").document(restaurant_id)

        if not restaurant_id:
            return Response({"error": "restaurant_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        foods.update({
            "name": name,
            "description": description,
            "category": category,
            "price": price,
            "available": True,
            "preparation_time": preparation_time,
            "image": image,
            "restaurant_id": restaurant_ref,
        })
        return Response({"message": "Food updated successfully"}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        available = request.data.get("available", True)
        foods = db.collection("foods").document(pk)
        foods.update({"available": available})
        return Response({"message": "Food availability updated successfully"}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        foods = db.collection("foods").document(pk)
        foods.update({"state": False})
        return Response({"message": "Food deleted successfully"}, status=status.HTTP_200_OK)
