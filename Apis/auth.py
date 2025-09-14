from flask import Flask ##Esta libreria es para crear la API, nos permite levantar un servidor web y definir el puerto para manejar solicitudes HTTP.
from pymongo import MongoClient ##Esta libreria es para conectarnos a MongoDB, nos permite interactuar con la base de datos, realizar consultas y manejar datos.

app = Flask(__name__) ##Crea una instancia de la aplicación Flask, que es el núcleo de nuestra API.

client = MongoClient("mongodb://localhost:27017/") ##Establece una conexión con el servidor de MongoDB que se está ejecutando en localhost en el puerto 27017.
db = client["profesores_db"] ##Selecciona la base de datos llamada "profesores_db".
profesores = db["profesores"]  ##Selecciona la colección llamada "profesores" dentro de la base de datos.

@app.route("/profesores", methods=["GET"]) ##Define una ruta en la API que responde a solicitudes GET en la URL "/profesores".
def get_profesores(): ##Define la función que se ejecuta cuando se accede a la ruta "/profesores".
  ##Logica para obtener todos los documentos de la colección "profesores" y devolverlos en formato JSON.
    data = list(profesores.find({}, {"_id": 0}))
    return {"profesores": data}
##esto solo se ejecuta si el archivo es ejecutado directamente en la maquina "local", no cuando es importado como un módulo en otro archivo.
if __name__ == "__main__":
    app.run(port=5002)