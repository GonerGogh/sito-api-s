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
        print("User from DB:", username)  # 🔹 debug
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
    
# Cambiar contraseña SIN pedir old_password
@app.route("/cambiarContra", methods=["POST"])
def change_password():
    data = request.json
    matricula = data.get("matricula")
    new_password = data.get("new_password")

    if not matricula or not new_password:
        return jsonify({"error": "Se requieren matricula y new_password"}), 400

    # Buscar usuario
    user = users.find_one({"username": matricula})
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Actualizar con nueva contraseña
    hashed_new_pw = generate_password_hash(new_password)
    users.update_one(
        {"username": matricula},
        {"$set": {"password": hashed_new_pw}}
    )

    return jsonify({"msg": "Contraseña actualizada correctamente"}), 200

@app.route("/users/<username>", methods=["DELETE"])
def delete_user(username):
    try:
        result = users.delete_one({"username": username})
        if result.deleted_count == 0:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        return jsonify({"msg": "Usuario eliminado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == "__main__":
    app.run(port=5002, debug=True)
