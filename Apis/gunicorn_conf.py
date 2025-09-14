# gunicorn_conf.py
import app # Importa tu archivo app.py para acceder a la función cargar_rostros

def post_worker_init(worker):
    """
    Este hook se ejecuta una vez en cada proceso worker después de que el worker ha arrancado.
    Es el lugar ideal para inicializar cosas que necesitan estar listas antes de que el worker
    comience a manejar peticiones, como la carga de encodings.
    """
    print("DEBUG (Gunicorn Hook): Inicializando worker después de arrancar.")
    try:
        app.cargar_rostros()
        print("DEBUG (Gunicorn Hook): Carga inicial de rostros completada en worker.")
    except Exception as e:
        print(f"CRITICAL ERROR (Gunicorn Hook): Fallo en la carga inicial de rostros en worker: {e}")
        # En un escenario de producción, aquí podrías decidir cómo manejar este error crítico,
        # como forzar al worker a salir si la inicialización es vital.
