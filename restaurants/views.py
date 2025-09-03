from backend_fidelizaciones.enums import RoleEnum
from firebase_config import db
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
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
        website = request.data.get("website", "")
        opening_hours = request.data.get("opening_hours", "")
        price_range = request.data.get("price_range", "")
        image = request.data.get("image", "")
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
            "image": image,
            "website": website,
            "opening_hours": opening_hours,
            "price_range": price_range,
            "address": address,
            "tags": tags,
            "rate": 4.5,
            "active": False
        })

        return Response({"message": "Restaurant created successfully"}, status=status.HTTP_201_CREATED)

    def get(self, request):
            restaurant_id = request.query_params.get("restaurant_id", None)
            active = request.query_params.get("active", True)
            response = []
            if restaurant_id:
                doc = db.collection("restaurants").document(restaurant_id).get()
                if not doc.exists:
                    return Response(
                        {"error": "Restaurant not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                restaurants = [doc]
            else:
                if active == 'false':
                    active = False
                restaurants = db.collection("restaurants").where("active", "==", active).stream()
            for restaurant in restaurants:
                restaurant_ref = db.collection("restaurants").document(restaurant.id)
                foods = db.collection("foods").where("restaurant_id", "==", restaurant_ref).stream()
                foods_list = []
                for food in foods:
                    food_dict = food.to_dict()
                    clean_firestore_data(food_dict)
                    food_dict["id"] = food.id
                    foods_list.append(food_dict)
                phone_number = None
                user_ref = restaurant.to_dict().get("user")
                if user_ref:
                    user = user_ref.get()
                    if user.exists:
                        phone_number = user.to_dict().get("phone_number")
                restaurant_data = restaurant.to_dict()
                clean_firestore_data(restaurant_data)
                restaurant_data["id"] = restaurant.id
                restaurant_data["phone_number"] = phone_number
                restaurant_data["foods"] = foods_list

                response.append(restaurant_data)

            return Response(
                {"message": "Restaurants list", "data": response},
                status=status.HTTP_200_OK
            )

    def put(self, request, restaurant_id):
        name = request.data.get("name", "")
        owner_name = request.data.get("owner_name", "")
        description = request.data.get("description", "")
        website = request.data.get("website", "")
        opening_hours = request.data.get("opening_hours", "")
        price_range = request.data.get("price_range", "")
        password = request.data.get("password", "")
        image = request.data.get("image", "")
        email = request.data.get("email", "")
        phone_number = request.data.get("phone_number", "")
        tags = request.data.get("tags", [])
        address = request.data.get("address", "")

        restaurant_ref = db.collection("restaurants").document(restaurant_id)
        restaurant = restaurant_ref.get()

        if not restaurant.exists:
            return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)

        user_ref = restaurant.to_dict().get("user")
        if password:
            user = auth.get_user_by_email(email)
            auth.update_user(
                user.uid,
                password=password
            )
        if not user_ref:
            return Response({"error": "User not found for this restaurant"}, status=status.HTTP_404_NOT_FOUND)

        user = user_ref.get()
        if not user.exists:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        user_ref.update({
            "name": owner_name,
            "email": email,
            "phone_number": phone_number,
            "address": address,
        })

        restaurant_ref.update({
            "name": name,
            "description": description,
            "image": image,
            "website": website,
            "opening_hours": opening_hours,
            "price_range": price_range,
            "address": address,
            "tags": tags,
        })

        return Response({"message": "Restaurant updated successfully"}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'], url_path='activate')
    def active(self, request, restaurant_id):
        restaurant_ref = db.collection("restaurants").document(restaurant_id)
        restaurant_doc = restaurant_ref.get()
        if not restaurant_doc.exists:
            return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)
        current_status = restaurant_doc.to_dict().get("active", False)
        new_status = not current_status
        restaurant_ref.update({"active": new_status})
        return Response(
            {
                "message": f"Restaurant {'activated' if new_status else 'deactivated'} successfully",
                "active": new_status
            },
            status=status.HTTP_200_OK
        )

