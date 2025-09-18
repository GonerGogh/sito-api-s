from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import requests

app = Flask(__name__)
CORS(app)

# Conexión a Mongo (Alumnado)
client = MongoClient("mongodb+srv://admin:123@sito.xzf6zex.mongodb.net/?retryWrites=true&w=majority&appName=Sito")
db = client["sito_servicios"]
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

@app.route("/alumnos/<matricula>/calificaciones", methods=["GET"])
def obtener_calificaciones(matricula):
    """
    Obtiene las calificaciones de un alumno y las devuelve como un diccionario.
    """
    alumno = alumnos.find_one({"matricula": matricula}, {"_id": 0, "calificaciones": 1})
    if not alumno:
        return jsonify({"error": "Alumno no encontrado"}), 404
    # Devuelve el objeto de calificaciones directamente
    return jsonify({"calificaciones": alumno.get("calificaciones", {})}), 200


# 📌 Subir o actualizar calificación de un alumno (lo usa Profesores)
@app.route("/alumnos/<matricula>/calificaciones", methods=["POST"])
def subir_calificacion(matricula):
    data = request.json
    print(matricula)

    grupo = data.get("grupo")
    calificacion = data.get("calificacion")
    profesor = data.get("profesor")

    alumno = alumnos.find_one({"matricula":matricula})
    print(alumno)
    if not alumno:
        return jsonify({"error": "Alumno no encontrado"}), 404

    # Actualiza usando notación de clave dinámica
    alumnos.update_one(
        {"matricula": matricula},
        {"$set": {
            f"calificaciones.{grupo}": {
                "profesor": profesor,
                "calificacion": calificacion
            }
        }}
    )

    return jsonify({"msg": f"Calificación registrada/actualizada para {matricula} en {grupo}"}), 200
import requests

@app.route("/alumnos/<matricula>/cambiar_contrasena", methods=["POST"])
def cambiar_contrasena(matricula):
    data = request.json
    nueva = data.get("nueva_contrasena")
    print("Datos recibidos en Alumnos:", data)

    if not nueva:
        return jsonify({"error": "Se requiere nueva_contrasena"}), 400

    try:
        r = requests.post(
            f"{AUTH_URL}/cambiarContra",
            json={                   # <-- así se pasa correctamente
                "matricula": matricula,
                "new_password": nueva
            },
            timeout=5
        )
        print("Payload enviado a Auth:", {"matricula": matricula, "new_password": nueva})
        print("Respuesta de Auth:", r.text)

        # Reenvía la respuesta de Auth tal cual
        try:
            resp_json = r.json()
        except ValueError:
            resp_json = {"error": "Auth respondió sin JSON", "content": r.text}

        return jsonify(resp_json), r.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Error comunicándose con Auth", "detalle": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5004, debug=True)
