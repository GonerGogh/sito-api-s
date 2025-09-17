from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import requests


app = Flask(__name__)
CORS(app)

# Conexión a Mongo (Servicios Escolares)
client = MongoClient("mongodb+srv://gonergogh:123@sito.xzf6zex.mongodb.net/?retryWrites=true&w=majority&appName=Sito")   
db = client["sito_profesores"]

# URL del microservicio Auth
AUTH_URL = "http://localhost:5002"  # cambia el puerto si tu Auth usa otro


#  Registrar profesor
@app.route("/profesoresR", methods=["POST"])
def registrar_profesor():
    data = request.json

    # Crear usuario en Auth primero
    user_payload = {
        "username": data["matricula"],
        "password": data["matricula"],  # o default "12345"
        "role": "profesor"
    }
    try:
        r = requests.post(f"{AUTH_URL}/register", json=user_payload)
        print(r.status_code, r.text)

        if r.status_code != 201:
            return jsonify({"msg": "No se pudo crear el usuario en Auth", "error": r.json()}), 500
    except Exception as e:
        return jsonify({"msg": "No se pudo comunicar con Auth", "error": str(e)}), 500

    # Si Auth fue exitoso, guardar en la colección profesor
    try:
        profesor = {
            "nombreP": data["nombre"],
            "matriculaP": data["matricula"],
            "grupos":[]
        }
        db.profesores.insert_one(profesor)
    except Exception as e:
        # Rollback: eliminar usuario creado en Auth si falla MongoDB
        requests.delete(f"{AUTH_URL}/profesores/{data['matricula']}")
        return jsonify({"msg": "No se pudo registrar el alumno en DB", "error": str(e)}), 500

    return jsonify({"msg": "Profesor registrado con usuario en Auth"}), 201

# Eliminar profesor
@app.route("/profesores", methods=["DELETE"])
def eliminar_profesor():
    matricula = request.args.get("matricula")
    if not matricula:
        return jsonify({"msg": "Falta matrícula"}), 400

    # Eliminar de Auth primero
    try:
        r = requests.delete(f"{AUTH_URL}/users/{matricula}")
        if r.status_code != 200:
            return jsonify({"msg": "No se pudo eliminar el usuario en Auth", "error": r.json()}), 500
    except Exception as e:
        return jsonify({"msg": "No se pudo comunicar con Auth", "error": str(e)}), 500

    # Si Auth fue exitoso, eliminar de la colección profesores
    result = db.profesores.delete_one({"matricula": matricula})
    if result.deleted_count == 0:
        return jsonify({"msg": "No se encontró el profesor en DB"}), 404

    return jsonify({"msg": "Profesor eliminado de Auth y DB"}), 200

@app.route("/profesoresGet", methods=["GET"])
def listar_profesores():
    profesores = list(db.profesores.find({}, {"_id": 0}))
    return jsonify(profesores), 200 



if __name__ == "__main__":
    app.run(port=5004, debug=True)
