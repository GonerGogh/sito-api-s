from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import requests

app = Flask(__name__)
CORS(app)

# Conexión a Mongo (Alumnado)
client = MongoClient("mongodb+srv://dieguino:123@sito.xzf6zex.mongodb.net/?retryWrites=true&w=majority&appName=Sito")
db = client["sito_alumnos"]
alumnos = db["alumnos"]

# URL del microservicio Auth
AUTH_URL = "http://localhost:5002"


# 📌 Consultar calificaciones de un alumno
@app.route("/alumnos/<matricula>/calificaciones", methods=["GET"])
def obtener_calificaciones(matricula):
    alumno = alumnos.find_one({"matricula": matricula}, {"_id": 0})
    if not alumno:
        return jsonify({"error": "Alumno no encontrado"}), 404
    return jsonify({"calificaciones": alumno.get("calificaciones", [])}), 200

# 📌 Subir o actualizar calificación de un alumno (lo usa Profesores)
@app.route("/alumnos/<matricula>/calificaciones", methods=["POST"])
def subir_calificacion(matricula):
    data = request.json
    grupo = data.get("grupo")
    calificacion = data.get("calificacion")
    profesor = data.get("profesor")

    alumno = alumnos.find_one({"matricula": matricula})
    if not alumno:
        return jsonify({"error": "Alumno no encontrado"}), 404

    calificaciones = alumno.get("calificaciones", [])
    existente = next((c for c in calificaciones if c["grupo"] == grupo), None)

    if existente:
        alumnos.update_one(
            {"matricula": matricula, "calificaciones.grupo": grupo},
            {"$set": {
                "calificaciones.$.calificacion": calificacion,
                "calificaciones.$.profesor": profesor
            }}
        )
    else:
        alumnos.update_one(
            {"matricula": matricula},
            {"$push": {
                "calificaciones": {
                    "grupo": grupo,
                    "profesor": profesor,
                    "calificacion": calificacion
                }
            }}
        )

    return jsonify({"msg": f"Calificación registrada/actualizada para {matricula} en {grupo}"}), 200

# 📌 Cambiar contraseña (llama a Auth)
@app.route("/alumnos/<matricula>/cambiar_contrasena", methods=["POST"])
def cambiar_contrasena(matricula):
    data = request.json
    nueva = data.get("nueva_contrasena")

    # Llamar microservicio Auth para cambiar contraseña
    try:
        r = requests.post(f"{AUTH_URL}/cambiar_contrasena", json={
            "username": matricula,
            "new_password": nueva
        })
        if r.status_code != 200:
            return jsonify({"error": "No se pudo cambiar contraseña en Auth", "detalle": r.json()}), 500
    except Exception as e:
        return jsonify({"error": "Error comunicándose con Auth", "detalle": str(e)}), 500

    return jsonify({"msg": f"Contraseña cambiada para {matricula}"}), 200

if __name__ == "__main__":
    app.run(port=5004, debug=True)
