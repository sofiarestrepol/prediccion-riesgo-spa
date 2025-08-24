import pandas as pd
import os, traceback, requests
# from database import SessionLocal
# from sqlalchemy.orm import Session
from config import DATABASE_CONFIG
import psycopg2

def traceback_error(e):
    """
    Extrae y formatea información detallada de la traza de una excepción.

    Parámetros:
        - e (Exception): Excepción de la cual se extraerá la traza.

    Retorna:
        - str: Una cadena formateada que contiene información sobre el tipo de excepción,
               el mensaje de la excepción y la línea de código donde ocurrió el error.
    """
    # Extrae la traza de la excepción
    tb = traceback.extract_tb(e.__traceback__)
    # Obtener la última entrada de la traza (donde ocurrió el error)
    filename, line, func, text = tb[-1]
    # Obtiene solo el nombre del archivo
    filename = os.path.basename(filename)
    # Formatea el mensaje de error con información detallada
    return f'Ocurrió un error en la línea {line} en el archivo {filename}. {type(e).__name__}: {e}'



# def get_db():
#     """
#     Genera una sesión de base de datos SQLAlchemy proporcionada como generador.

#     Retorna:
#         - Session: Una sesión de SQLAlchemy configurada para la base de datos.
#     """
#     #  Crea una nueva instancia de sesión para la base de datos
#     db = SessionLocal()
#     try:
#         # Yield permite devolver la sesión de SQLAlchemy como un generador, apra ser utilziada en otras partes del código
#         yield db
#     finally:
#         # La sesión se cierra automáticamente después de su uso
#         db.close()







    
# def create_record_in_db(model, data: dict, db: Session):
#     """
#     Crea y guarda un nuevo registro en la base de datos.

#     Paramétros::
#         - model: Modelo de SQLAlchemy en el cual se guardarán los datos.
#         - data (dict): Datos del registro a crear.
#         - db (Session): Sesión de la base de datos.

#     Retorna:
#         - new_record: El nuevo registro creado y guardado en la base de datos.
#     """
#     try:
#         # Crea un nuevo objeto del modelo con los datos recibidos
#         new_record = model(**data)
#         # Agrega el nuevo registro a la base de datos
#         db.add(new_record)
#         db.commit()
#         db.refresh(new_record)
#     except Exception as e:
#         print("ERROR AL GUARDAR EN LA BASE DE DATOS:")
#         traceback.print_exc()
#         raise


def create_user_supabase(data: dict):
    """
    Envía un nuevo registro a la tabla `users` en Supabase usando la REST API.
    """
    url = f"{DATABASE_CONFIG['SUPABASE_URL']}/rest/v1/users"

    headers = {
        "apikey": DATABASE_CONFIG["SUPABASE_SERVICE_KEY"],
        "Authorization": f"Bearer {DATABASE_CONFIG['SUPABASE_SERVICE_KEY']}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # lanza error si el status != 200
        return response.json()

    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Connection Error:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Request Exception:", err)

    return None




