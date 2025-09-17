from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import requests

app = Flask(__name__)
CORS(app)

# Conexión a Mongo (Servicios Escolares)
client = MongoClient("mongodb://localhost:27017/")
db = client["sito_servicios"]

# URL del microservicio Auth
AUTH_URL = "http://localhost:5002"  # cambia el puerto si tu Auth usa otro


@app.route("/alumnos", methods=["POST"])
def registrar_alumno():
    data = request.json

    # Guardar en la colección alumnos
    alumno = {
        "nombre": data["nombre"],
        "matricula": data["matricula"],
        "carrera": data.get("carrera")
    }
    db.alumnos.insert_one(alumno)

    # Crear usuario en Auth
    user_payload = {
        "username": data["matricula"],
        "password": data["matricula"],  # puedes usar default "12345" y que después lo cambien
        "role": "alumno"
    }
    try:
        r = requests.post(f"{AUTH_URL}/register", json=user_payload)
        if r.status_code != 201:
            return jsonify({"msg": "Alumno creado pero fallo Auth", "error": r.json()}), 500
    except Exception as e:
        return jsonify({"msg": "Alumno creado pero no se pudo comunicar con Auth", "error": str(e)}), 500

    return jsonify({"msg": "Alumno registrado con usuario en Auth"}), 201

# 📌 Listar alumnos
@app.route("/alumnos", methods=["GET"])
def listar_alumnos():
    result = list(alumnos.find({}, {"_id": 0}))
    return jsonify(result)

# 📌 Registrar grupo
@app.route("/grupos", methods=["POST"])
def registrar_grupo():
    data = request.json
    nombre = data.get("nombre_grupo")

    if grupos.find_one({"nombre_grupo": nombre}):
        return jsonify({"error": "Grupo ya existe"}), 400

    grupos.insert_one({
        "nombre_grupo": data["nombre_grupo"],
        "carrera": data["carrera"],
        "profesor_responsable": data["profesor_responsable"],
        "alumnos": []
    })
    return jsonify({"msg": "Grupo registrado con éxito"}), 201

# 📌 Listar grupos
@app.route("/grupos", methods=["GET"])
def listar_grupos():
    result = list(grupos.find({}, {"_id": 0}))
    return jsonify(result)

# 📌 Agregar alumno a grupo
@app.route("/grupos/<nombre_grupo>/agregar", methods=["POST"])
def agregar_alumno_a_grupo(nombre_grupo):
    data = request.json
    matricula = data.get("matricula")

    grupo = grupos.find_one({"nombre_grupo": nombre_grupo})
    if not grupo:
        return jsonify({"error": "Grupo no encontrado"}), 404

    if matricula in grupo["alumnos"]:
        return jsonify({"error": "Alumno ya está en el grupo"}), 400

    grupos.update_one(
        {"nombre_grupo": nombre_grupo},
        {"$push": {"alumnos": matricula}}
    )
    return jsonify({"msg": f"Alumno {matricula} agregado al grupo {nombre_grupo}"}), 200

if __name__ == "__main__":
    app.run(port=5003, debug=True)