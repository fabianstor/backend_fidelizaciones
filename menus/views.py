from firebase_config import db
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class MenusView(APIView):

    def post(self, request):
        name = request.data.get("name")
        description = request.data.get("description")
        restaurant_id = request.data.get("restaurant_id")
        foods = request.data.get("foods", [])
        menu = db.collection("menus")

        menu.add({
            "name": name,
            "description": description,
            "restaurant_id": restaurant_id,
            "foods": foods
        })
        return Response({"message": "Menu created successfully"}, status=status.HTTP_201_CREATED)


    def get(self, request):
        restaurant_id = request.query_params.get("restaurant_id")
        restaurant_ref = db.collection("restaurants").document(restaurant_id)
        menus = db.collection("menus").where("restaurant", "==", restaurant_ref).stream()
        if not menus:
            return Response({"message": "No menus found"}, status=status.HTTP_404_NOT_FOUND)
        response = []
        for menu in menus:
            menu_data = menu.to_dict()
            menu_data.pop("restaurant", None)
            response.append({
                "id": menu.id,
                "data": menu_data
            })
        return Response(response, status=status.HTTP_200_OK)

    def put(self, request, menu_id):
        name = request.data.get("name")
        description = request.data.get("description")
        restaurant_id = request.data.get("restaurant_id")
        foods = request.data.get("foods", [])

        menu = db.collection("menus").document(menu_id)
        menu.update({
            "name": name,
            "description": description,
            "restaurant_id": restaurant_id,
            "foods": foods
        })
        return Response({"message": "Menu updated successfully"}, status=status.HTTP_200_OK)
