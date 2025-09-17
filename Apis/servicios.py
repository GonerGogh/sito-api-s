from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import requests

app = Flask(__name__)
CORS(app)

# Conexión a Mongo (Servicios Escolares)
client = MongoClient("mongodb+srv://dieguino:123@sito.xzf6zex.mongodb.net/?retryWrites=true&w=majority&appName=Sito")
db = client["sito_servicios"]
# URL del microservicio Auth
AUTH_URL = "http://localhost:5002"  # cambia el puerto si tu Auth usa otro

# 📌 Registrar alumno
@app.route("/alumnosR", methods=["POST"])
def registrar_alumno():
    data = request.json

    # Crear usuario en Auth primero
    user_payload = {
        "username": data["matricula"],
        "password": data["matricula"],  # o default "12345"
        "role": "alumno"
    }
    try:
        r = requests.post(f"{AUTH_URL}/register", json=user_payload)
        print(r.status_code, r.text)

        if r.status_code != 201:
            return jsonify({"msg": "No se pudo crear el usuario en Auth", "error": r.json()}), 500
    except Exception as e:
        return jsonify({"msg": "No se pudo comunicar con Auth", "error": str(e)}), 500

    # Si Auth fue exitoso, guardar en la colección alumnos
    try:
        alumno = {
            "nombre": data["nombre"],
            "matricula": data["matricula"],
            "carrera": data.get("carrera")
        }
        db.alumnos.insert_one(alumno)
    except Exception as e:
        # Rollback: eliminar usuario creado en Auth si falla MongoDB
        requests.delete(f"{AUTH_URL}/users/{data['matricula']}")
        return jsonify({"msg": "No se pudo registrar el alumno en DB", "error": str(e)}), 500

    return jsonify({"msg": "Alumno registrado con usuario en Auth"}), 201

# 📌 Listar alumnos
@app.route("/alumnosL", methods=["GET"])
def listar_alumnos():
    alumnos = list(db.alumnos.find({}, {"_id": 0}))
    return jsonify(alumnos), 200

# 📌 Registrar grupo
@app.route("/gruposR", methods=["POST"])
def registrar_grupo():
    data = request.json
    nombre = data.get("nombre_grupo")

    if db.grupos.find_one({"nombre_grupo": nombre}):
        return jsonify({"error": "Grupo ya existe"}), 400

    db.grupos.insert_one({
        "nombre_grupo": data["nombre_grupo"],
        "carrera": data["carrera"],
        "profesor_responsable": data["profesor_responsable"],
        "alumnos": []
    })
    return jsonify({"msg": "Grupo registrado con éxito"}), 201

# 📌 Listar grupos
@app.route("/gruposL", methods=["GET"])
def listar_grupos():
    grupos = list(db.grupos.find({}, {"_id": 0}))
    return jsonify(grupos), 200

# 📌 Agregar alumno a grupo
@app.route("/grupos/<nombre_grupo>/agregar", methods=["POST"])
def agregar_alumno_a_grupo(nombre_grupo):
    data = request.json
    matricula = data.get("matricula")

    grupo = db.grupos.find_one({"nombre_grupo": nombre_grupo})
    if not grupo:
        return jsonify({"error": "Grupo no encontrado"}), 404

    if matricula in grupo["alumnos"]:
        return jsonify({"error": "Alumno ya está en el grupo"}), 400

    db.grupos.update_one(
        {"nombre_grupo": nombre_grupo},
        {"$push": {"alumnos": matricula}}
    )
    return jsonify({"msg": f"Alumno {matricula} agregado al grupo {nombre_grupo}"}), 200

# 📌 Listar profesores
@app.route("/profesoresL", methods=["GET"])
def listar_profesores():
    try:
        # Supongamos que tu microservicio de RH está corriendo en localhost:5005
        res = requests.get("http://localhost:5005/profesoresL")
        if res.status_code == 200:
            return jsonify(res.json()), 200
        else:
            return jsonify({"error": "No se pudieron obtener los profesores"}), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    app.run(port=5003, debug=True)
