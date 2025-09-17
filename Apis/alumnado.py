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
AUTH_URL_S = "http://localhost:5003"  # cambia el puerto si tu Auth usa otro

# 📌 Consultar los grupos a los que pertenece un alumno
@app.route("/alumnos/<matricula>/grupo", methods=["GET"])
def obtener_grupos_de_alumno(matricula):
    try:
        # 1. Conectar al microservicio de Grupos
        # Asegúrate de que esta URL sea la correcta para tu servicio de grupos
        # Ejemplo: AUTH_URL_S = "http://localhost:5003" si está en el puerto 5003
        r = requests.get(f"{AUTH_URL_S}/gruposL")

        if r.status_code != 200:
            return jsonify({"error": "No se pudo obtener la lista de grupos", "detalle": r.json()}), 500

        # 2. Obtener la lista de todos los grupos del microservicio de grupos
        grupos_completos = r.json()

        # 3. Filtrar los grupos para encontrar aquellos que contienen la matrícula del alumno
        grupos_del_alumno = []
        for grupo in grupos_completos:
            if "alumnos" in grupo and matricula in grupo["alumnos"]:
                # Se agrega solo la información relevante del grupo, no la lista de todos los alumnos
                grupos_del_alumno.append({
                    "nombre_grupo": grupo["nombre_grupo"],
                    "carrera": grupo["carrera"],
                    "profesor_responsable": grupo["profesor_responsable"]
                })

        if not grupos_del_alumno:
            return jsonify({"msg": "Alumno no encontrado en ningún grupo"}), 404

        return jsonify(grupos_del_alumno), 200

    except Exception as e:
        return jsonify({"error": "Error de comunicación con el servicio de grupos", "detalle": str(e)}), 500


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

# 📌 Agregar calificación nueva (no sobreescribe, solo agrega)
@app.route("/alumnos/<matricula>/agregar_calificacion", methods=["POST"])
def agregar_calificacion(matricula):
    data = request.json
    grupo = data.get("grupo")
    calificacion = data.get("calificacion")
    profesor = data.get("profesor")

    alumno = alumnos.find_one({"matricula": matricula})
    if not alumno:
        return jsonify({"error": "Alumno no encontrado"}), 404

    # Siempre insertar una nueva calificación aunque exista ya una del mismo grupo
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

    return jsonify({"msg": f"Calificación agregada para {matricula} en {grupo}"}), 201

if __name__ == "__main__":
    app.run(port=5004, debug=True)
