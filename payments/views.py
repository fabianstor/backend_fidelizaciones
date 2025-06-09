from firebase_config import db
from rest_framework.views import APIView
from rest_framework.response import Response


class PaymentsView(APIView):

    def post(self, request):
        cvv = request.POST.get("cvv", "")
        card_number = request.POST.get("card_number", "")
        expiration_date = request.POST.get("expiration_date", "")
        owner = request.POST.get("owner", "")
        restaurant_id = request.POST.get("restaurant_id", "")
        user_id = request.POST.get("user_id", "")
        foods = request.POST.get("foods", [])
        amount = request.POST.get("amount", "")

        payments = db.collection("payments")
        payments.add({
            "cvv": cvv,
            "card_number": card_number,
            "expiration_date": expiration_date,
            "owner": owner,
            "restaurant_id": restaurant_id,
            "user_id": user_id,
            "foods": foods,
            "amount": amount
        })

        return Response({"message": "Payment created successfully"}, status=201)

    def get(self, request):
        payments = db.collection("payments").stream()
        response = []

        for payment in payments:
            payment_dict = payment.to_dict()
            payment_dict["id"] = payment.id
            response.append(payment_dict)

        return Response({"message": "Payments list", "data": response}, status=200)

    def put(self, request, payment_id):
        cvv = request.POST.get("cvv", "")
        card_number = request.POST.get("card_number", "")
        expiration_date = request.POST.get("expiration_date", "")
        owner = request.POST.get("owner", "")
        restaurant_id = request.POST.get("restaurant_id", "")
        user_id = request.POST.get("user_id", "")
        foods = request.POST.get("foods", [])
        amount = request.POST.get("amount", "")

        payment_ref = db.document(f"payments/{payment_id}")
        payment_ref.update({
            "cvv": cvv,
            "card_number": card_number,
            "expiration_date": expiration_date,
            "restaurant_id": restaurant_id,
            "user_id": user_id,
            "foods": foods,
            "owner": owner,
            "amount": amount
        })

        return Response({"message": "Payment updated successfully"}, status=200)
