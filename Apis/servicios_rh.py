from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import requests


app = Flask(__name__)
CORS(app)

# Conexión a Mongo (Servicios Escolares)
client = MongoClient("mongodb+srv://admin:123@sito.xzf6zex.mongodb.net/?retryWrites=true&w=majority&appName=Sito")   
db = client["sito_profesores"]

# URL del microservicio Auth
AUTH_URL = "http://localhost:5002"  # cambia el puerto si tu Auth usa otro


#  Registrar profesor
@app.route("/profesoresR", methods=["POST"])
def registrar_profesor():
    data = request.json or {}

    # Validación básica de entrada
    nombreP = data.get("nombreP", "").strip()
    matriculaP = data.get("matriculaP", "").strip()
    if not nombreP or not matriculaP:
        return jsonify({"msg": "Faltan campos requeridos: nombreP y matriculaP"}), 400

    # Evitar duplicados en DB antes de crear en Auth
    if db.profesores.find_one({"matriculaP": matriculaP}):
        return jsonify({"msg": "La matrícula ya existe en profesores"}), 409

    # Crear usuario en Auth primero
    user_payload = {
        "username": matriculaP,
        "password": matriculaP,  # usa la matrícula como password
        "role": "profesor"
    }
    
    try:
        print(f"Intentando registrar en Auth: {user_payload}")
        r = requests.post(f"{AUTH_URL}/register", json=user_payload, timeout=10)
        print(f"Respuesta de Auth - Status: {r.status_code}, Content: {r.text}")

        if r.status_code == 201:
            # Auth exitoso, continuar con MongoDB
            try:
                profesor = {
                    "nombreP": nombreP,
                    "matriculaP": matriculaP,
                    "grupos": []
                }
                db.profesores.insert_one(profesor)
                return jsonify({"msg": "Profesor registrado exitosamente"}), 201
                
            except Exception as e:
                # Rollback: eliminar usuario creado en Auth si falla MongoDB
                try:
                    requests.delete(f"{AUTH_URL}/users/{matriculaP}", timeout=5)
                except Exception:
                    pass
                return jsonify({"msg": "Error al guardar en BD de profesores", "error": str(e)}), 500
                
        elif r.status_code == 400:
            # Usuario ya existe en Auth
            try:
                auth_response = r.json()
                return jsonify({"msg": "El usuario ya existe en el sistema", "error": auth_response}), 409
            except Exception:
                return jsonify({"msg": "El usuario ya existe en el sistema", "error": r.text}), 409
                
        else:
            # Otro error de Auth
            try:
                auth_response = r.json()
                return jsonify({"msg": "Error al crear usuario en Auth", "error": auth_response}), 502
            except Exception:
                return jsonify({"msg": "Error al crear usuario en Auth", "error": r.text}), 502
                
    except requests.exceptions.Timeout:
        return jsonify({"msg": "Timeout al comunicarse con el servicio Auth"}), 502
    except requests.exceptions.ConnectionError:
        return jsonify({"msg": "No se pudo conectar con el servicio Auth. ¿Está ejecutándose en puerto 5002?"}), 502
    except Exception as e:
        return jsonify({"msg": "Error inesperado al comunicarse con Auth", "error": str(e)}), 502
    data = request.json or {}

    # Validación básica de entrada
    nombreP = data.get("nombreP", "").strip()
    matriculaP = data.get("matriculaP", "").strip()
    if not nombreP or not matriculaP:
        return jsonify({"msg": "Faltan campos requeridos: nombreP y matriculaP"}), 400

    # Evitar duplicados en DB antes de crear en Auth
    if db.profesores.find_one({"matriculaP": matriculaP}):
        return jsonify({"msg": "La matrícula ya existe en profesores"}), 409

    # Crear usuario en Auth primero
    user_payload = {
        "username": matriculaP,
        "password": matriculaP,  # o default "12345"
        "role": "profesor"
    }
    try:
        r = requests.post(f"{AUTH_URL}/register", json=user_payload)
        print(r.status_code, r.text)

        if r.status_code != 201:
            # Propagar mensaje de Auth si viene en JSON
            try:
                auth_error = r.json()
            except Exception:
                auth_error = {"raw": r.text}
            return jsonify({"msg": "No se pudo crear el usuario en Auth", "error": auth_error}), 502
    except Exception as e:
        return jsonify({"msg": "No se pudo comunicar con Auth", "error": str(e)}), 502

    # Si Auth fue exitoso, guardar en la colección profesor
    try:
        profesor = {
            "nombreP": nombreP,
            "matriculaP": matriculaP,
            "grupos": []
        }
        db.profesores.insert_one(profesor)
    except Exception as e:
        # Rollback: eliminar usuario creado en Auth si falla MongoDB
        try:
            requests.delete(f"{AUTH_URL}/users/{matriculaP}")
        except Exception:
            pass
        return jsonify({"msg": "No se pudo registrar el profesor en DB", "error": str(e)}), 500

    return jsonify({"msg": "Profesor registrado con usuario en Auth"}), 201

# Eliminar profesor
@app.route("/profesores", methods=["DELETE"])
def eliminar_profesor():
    matricula = request.args.get("matriculaP")
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
    result = db.profesores.delete_one({"matriculaP": matricula})
    if result.deleted_count == 0:
        return jsonify({"msg": "No se encontró el profesor en DB"}), 404

    return jsonify({"msg": "Profesor eliminado de Auth y DB"}), 200

# Listar profesores
@app.route("/profesoresGet", methods=["GET"])
def listar_profesores():
    profesores = list(db.profesores.find({}, {"_id": 0}))
    return jsonify(profesores), 200 

# 📌 Asignar grupo a profesor
@app.route("/profesores/asignar_grupo", methods=["POST"])
def asignar_grupo_a_profesor():
    data = request.json
    matricula = data.get("matricula")  # matrícula del profesor
    grupo = data.get("grupo")

    prof = db.profesores.find_one({"matricula": matricula})
    if not prof:
        return jsonify({"error": "Profesor no encontrado"}), 404

    db.profesores.update_one(
        {"matricula": matricula},
        {"$push": {"grupos": grupo}}
    )

    return jsonify({"msg": f"Grupo {grupo} asignado al profesor {matricula}"}), 200


if __name__ == "__main__":
    app.run(port=5005, debug=True)
