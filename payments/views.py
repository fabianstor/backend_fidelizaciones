from firebase_config import db
from rest_framework.views import APIView
from rest_framework.response import Response
from google.cloud.firestore import DocumentReference
import random
import string


def generate_code():
    code = string.ascii_uppercase + string.digits
    code_start = ''.join(random.choices(code, k=3))
    code_end = ''.join(random.choices(code, k=3))
    return f"{code_start}-{code_end}"

def clean_firestore_data(data):
    """Convierte DocumentReference en string (id del doc) recursivamente"""
    if isinstance(data, dict):
        return {k: clean_firestore_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_firestore_data(v) for v in data]
    elif isinstance(data, DocumentReference):
        return data.id  # o data.path si quieres la ruta completa
    return data


class PaymentsView(APIView):

    def post(self, request):
        user_id = request.data.get("user_id")
        products = request.data.get("products", [])
        restaurant_id = request.data.get("restaurant_id")
        points = request.data.get("points", 0)
        amount = request.data.get("amount")

        if not products or not restaurant_id or amount is None:
            return Response({"error": "Faltan datos obligatorios"}, status=400)

        approval_code = generate_code()

        user_points = db.collection("user_points").where("user_id", "==", user_id).get()
        if user_points:
            doc = user_points[0]
            current_points = doc.to_dict().get("points", 0)
            db.collection("user_points").document(doc.id).update({"points": current_points - points})
        payment_data ={
            "user_id": user_id,
            "products": products,
            "restaurant_id": restaurant_id,
            "points": points,
            "approval_code": approval_code,
            "amount": amount,
            "status": "pending"
        }
        db.collection("payments").add(payment_data)
        return Response({"approval_code0": approval_code, "message": "Pago solicitado exitosamente"}, status=200)

    def put(self, request):
        approval_code = request.data.get("approval_code", None)
        approval = request.data.get("approval", False)
        if not approval_code:
            return Response({"error": "approval_code es obligatorio"}, status=400)
        docs = db.collection("payments").where("approval_code", "==", approval_code).stream()
        nuevo_estado = "approved" if approval else "rejected"
        for doc in docs:
            doc.reference.update({"status": nuevo_estado})
        payment_docs = db.collection("payments").where("approval_code", "==", approval_code).get()
        if not payment_docs:
            return Response({"error": "Pago no encontrado"}, status=404)
        payment = payment_docs[0].to_dict()
        amount = payment.get("amount", 0)
        user_id = payment.get("user_id")
        user_points_ref = db.collection("user_points").where("user_id", "==", user_id).get()
        points_to_add = amount * 0.01
        if user_points_ref:
            doc = user_points_ref[0]
            current_points = doc.to_dict().get("points", 0)
            new_points = current_points + points_to_add
            db.collection("user_points").document(doc.id).update({"points": new_points})
        else:
            db.collection("user_points").add({
                "user_id": user_id,
                "points": points_to_add,
            })
        return Response("Pago gestionado con éxito", status=200)


from rest_framework.response import Response
from google.cloud.firestore import DocumentReference

def clean_firestore_data(data):
    """Convierte DocumentReference en string (id del doc) recursivamente"""
    if isinstance(data, dict):
        return {k: clean_firestore_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_firestore_data(v) for v in data]
    elif isinstance(data, DocumentReference):
        return data.id  # o data.path si quieres la ruta completa
    return data


class PaymentDetailView(APIView):
    def get(self, request):
        pk = request.query_params.get("id", None)
        restaurant_id = request.query_params.get("restaurant_id", None)
        if not pk and not restaurant_id:
            return Response({"error": "id o restaurant_id es obligatorio"}, status=400)
        if pk:
            payment_doc = db.collection("payments").document(pk).get()
            if not payment_doc.exists:
                return Response({"error": "Pago no encontrado"}, status=404)

            payment_data = payment_doc.to_dict()
            payment_data["id"] = payment_doc.id
            if "products" in payment_data:
                full_products = []
                for product in payment_data["products"]:
                    product_id = product.get("product_id")
                    if product_id:
                        product_doc = db.collection("foods").document(product_id).get()
                        if product_doc.exists:
                            product_data = product_doc.to_dict()
                            product_data["id"] = product_doc.id
                            product.update(clean_firestore_data(product_data))
                    full_products.append(clean_firestore_data(product))
                payment_data["products"] = full_products

            payment_data = clean_firestore_data(payment_data)
            return Response(payment_data, status=200)
        if restaurant_id:
            payments = db.collection("payments").where("restaurant_id", "==", restaurant_id).stream()
            response = []
            for payment in payments:
                payment_data = payment.to_dict()
                payment_data["id"] = payment.id

                if "products" in payment_data:
                    full_products = []
                    for product in payment_data["products"]:
                        product_id = product.get("product_id")
                        if product_id:
                            product_doc = db.collection("foods").document(product_id).get()
                            if product_doc.exists:
                                product_data = product_doc.to_dict()
                                product_data["id"] = product_doc.id
                                product.update(clean_firestore_data(product_data))
                        full_products.append(clean_firestore_data(product))
                    payment_data["products"] = full_products

                response.append(clean_firestore_data(payment_data))

            return Response({"details": response}, status=200)