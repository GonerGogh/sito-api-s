from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
import requests

app = Flask(__name__)
CORS(app)

# Conexión a Mongo (Profesores)
client = MongoClient("mongodb+srv://admin:123@sito.xzf6zex.mongodb.net/?retryWrites=true&w=majority&appName=Sito")
db = client["sito_profesores"]
profesores = db["profesores"]

# URL microservicio Alumnado
ALUMNADO_URL = "http://localhost:5004"

# 📌 Listar profesores
@app.route("/profesoresL", methods=["GET"])
def listar_profesores():
    lista = list(profesores.find({}, {"_id": 0}))
    return jsonify(lista), 200

# 📌 Subir calificación a un alumno (formato calificaciones como objeto)
@app.route("/profesores/<matriculaP>/calificaciones", methods=["POST"])
def subir_calificacion(matriculaP):
    data = request.json
    matricula = data.get("matricula")
    grupo = data.get("grupo")
    calificacion = data.get("calificacion")

    profesor = profesores.find_one({"matriculaP": matriculaP})
    if not profesor:
        return jsonify({"error": "Profesor no encontrado"}), 404
    nombre_profesor = profesor.get("nombreP", matriculaP)

    try:
        r = requests.post(f"{ALUMNADO_URL}/alumnos/{matricula}/calificaciones", json={
            "grupo": grupo,
            "calificacion": calificacion,
            "profesor": nombre_profesor
        })
        if r.status_code not in [200, 201]:
            try:
                detalle = r.json()
            except:
                detalle = r.text
            return jsonify({"error": "Error subiendo calificación en Alumnado", "detalle": detalle}), 500
    except Exception as e:
        return jsonify({"error": "No se pudo comunicar con Alumnado", "detalle": str(e)}), 500

    return jsonify({"msg": f"Calificación agregada para {matricula} en {grupo} por {nombre_profesor}"}), 200

# 📌 Cambiar contraseña directamente sin llamar a Auth
@app.route("/profesores/<matriculaP>/cambiar_contrasena", methods=["POST"])
def cambiar_contrasena(matriculaP):
    data = request.json
    nueva = data.get("nueva_contrasena")

    profesor = profesores.find_one({"matriculaP": matriculaP})
    if not profesor:
        return jsonify({"error": "Profesor no encontrado"}), 404

    hashed_pw = generate_password_hash(nueva)
    profesores.update_one({"matriculaP": matriculaP}, {"$set": {"password": hashed_pw}})

    return jsonify({"msg": f"Contraseña cambiada para {matriculaP}"}), 200

if __name__ == "__main__":
    app.run(port=5005, debug=True)
