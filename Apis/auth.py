from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os

# Config
app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = "supersecreto"  # cámbialo por una env var

# Conexión a Mongo
client = MongoClient("mongodb+srv://dieguino:123@sito.xzf6zex.mongodb.net/?retryWrites=true&w=majority&appName=Sito")
db = client["sito_auth"]
users = db["users"]

# Registro de usuario
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    role = data.get("role") 
    print("Login attempt:", username, password)  # 🔹 debug

    if users.find_one({"username": username}):
        print("User from DB:", user)  # 🔹 debug
        return jsonify({"error": "Usuario ya existe"}), 400

    hashed_pw = generate_password_hash(password)
    users.insert_one({"username": username, "password": hashed_pw, "role": role})

    return jsonify({"msg": "Usuario registrado"}), 201

# Login
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = users.find_one({"username": username})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    # Generar token JWT
    token = jwt.encode(
        {
            "username": username,
            "role": user["role"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        },
        app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return jsonify({"token": token, "role": user["role"]})

# Ruta protegida de prueba
@app.route("/profile", methods=["GET"])
def profile():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Token requerido"}), 403

    try:
        decoded = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        return jsonify({"user": decoded["username"], "role": decoded["role"]})
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

if __name__ == "__main__":
    app.run(port=5002, debug=True)
