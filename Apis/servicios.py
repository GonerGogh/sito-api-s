from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import requests

app = Flask(__name__)
CORS(app)

# Conexión a Mongo (Servicios Escolares)
client = MongoClient("mongodb+srv://admin:123@sito.xzf6zex.mongodb.net/?retryWrites=true&w=majority&appName=Sito")
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
    profesor = data.get("profesor_responsable")

    if db.grupos.find_one({"nombre_grupo": nombre}):
        return jsonify({"error": "Grupo ya existe"}), 400

    # Insertar grupo en DB
    db.grupos.insert_one({
        "nombre_grupo": data["nombre_grupo"],
        "carrera": data["carrera"],
        "profesor_responsable": profesor,
        "alumnos": []
    })

    # 🔗 Asociar grupo al profesor en RH
    try:
        r = requests.post("http://localhost:5005/profesores/asignar_grupo", json={
            "profesor": profesor,
            "grupo": nombre
        })
        if r.status_code != 200:
            return jsonify({
                "msg": "Grupo creado, pero no se pudo asignar al profesor",
                "detalle": r.json()
            }), 207  # Multi-Status: parte exitosa, parte fallida
    except Exception as e:
        return jsonify({
            "msg": "Grupo creado, pero error comunicándose con RH",
            "detalle": str(e)
        }), 207

    return jsonify({"msg": "Grupo registrado con éxito y asignado al profesor"}), 201
# ... (código anterior)
# ... (código anterior)

# ... (código anterior)

# 📌 Listar grupos con nombre y matrícula del profesor
@app.route("/gruposL", methods=["GET"])
def listar_grupos():
    grupos = list(db.grupos.find({}, {"_id": 0}))

    # Llamamos al microservicio de RH para obtener todos los profesores
    try:
        res = requests.get("http://localhost:5005/profesoresGet")
        if res.status_code == 200:
            profesores = res.json()  # lista de dicts con {matriculaP, nombreP, ...}
            # Crea un mapa que asocia la matrícula con un diccionario que contiene el nombre y la matrícula
            mapa_profes = {p["matriculaP"]: {"nombre": p["nombreP"], "matricula": p["matriculaP"]} for p in profesores}

            # Reemplazar la matrícula por un objeto con nombre y matrícula en cada grupo
            for g in grupos:
                matricula = g.get("profesor_responsable")
                if matricula in mapa_profes:
                    g["profesor_responsable"] = mapa_profes[matricula]
                else:
                    g["profesor_responsable"] = {"nombre": "Profesor no encontrado", "matricula": matricula}
    except Exception as e:
        # Si falla RH, dejamos solo la matrícula
        print("Error comunicando con RH:", e)

    return jsonify(grupos), 200

# ... (código restante)
# ... (código restante)
# ... (código restante)
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
        res = requests.get("http://localhost:5005/profesoresGet")
        if res.status_code == 200:
            return jsonify(res.json()), 200
        else:
            return jsonify({"error": "No se pudieron obtener los profesores"}), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5003, debug=True)
