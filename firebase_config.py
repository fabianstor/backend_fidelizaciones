# users/firebase_config.py

import firebase_admin
from firebase_admin import credentials

# Inicializar Firebase solo si no está inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred)

from firebase_admin import firestore

# Acceder a Firestore
db = firestore.client()
