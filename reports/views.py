from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, timezone, timedelta
from firebase_config import db
from django.http import JsonResponse


class ReportsView(APIView):

    def get(self, request):
            restaurant_id = request.GET.get("restaurant_id")
            if not restaurant_id:
                return JsonResponse({"error": "restaurant_id es requerido"}, status=400)
            now = datetime.now(timezone.utc)
            start_of_day = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
            end_of_day = start_of_day + timedelta(days=1)
            payments_query = (
                db.collection("payments")
                .where("restaurant_id", "==", restaurant_id)
                .stream()
            )
            payments_of_the_day = [
                p.to_dict()
                for p in payments_query
                if p.to_dict().get("created_at")
                and start_of_day <= p.to_dict()["created_at"] <= end_of_day
            ]
            payments_of_the_day = [
                p for p in payments_of_the_day if p.get("status") == "completed"
            ]
            income_of_the_day = sum(p.get("amount", 0) for p in payments_of_the_day)
            orders_query = (
                db.collection("orders")
                .where("restaurant_id", "==", restaurant_id)
                .stream()
            )
            orders_of_the_day = [
                o.to_dict()
                for o in orders_query
                if o.to_dict().get("created_at")
                and start_of_day <= o.to_dict()["created_at"] <= end_of_day
            ]

            total_orders = len(orders_of_the_day)
            recent_payment_query = (
                db.collection("payments")
                .where("restaurant_id", "==", restaurant_id)
                .stream()
            )
            recent_payment = [doc.to_dict() for doc in recent_payment_query if doc.to_dict().get("created_at")]
            recent_payment = sorted(
                recent_payment,
                key=lambda x: x["created_at"],
                reverse=True
            )[:4]
            return JsonResponse({
                "income_of_the_day": income_of_the_day,
                "total_orders": total_orders,
                "recent_payment": recent_payment,
            })


class AdminReportsView(APIView):

    def get(self, request):
        users_count = db.collection("users").count().get()[0][0].value
        restaurants_count = db.collection("restaurants").count().get()[0][0].value
        payments = db.collection("payments").where  ("status", "==", "approved").stream()
        total_amount = sum(doc.to_dict().get("amount", 0) for doc in payments)
        pending_payments_count = db.collection("payments").where("status", "==", "pending").count().get()[0][0].value

        return Response({
            "users": users_count,
            "restaurants": restaurants_count,
            "total_amount": total_amount,
            "active_payments": pending_payments_count,
        }, status=200)
