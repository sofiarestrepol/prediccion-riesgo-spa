import traceback, os
import pandas as pd
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import exists
from joblib import load
from starlette import status
from dotenv import load_dotenv
from schemas import UserData
from services.interface_service import *
from services.dataframe_service import divide_dataset, setup_test_data, execute_expert_system, encode_column, load_model
from definitions import dict_rename_external_columns, prediction_columns, dict_renombrar_respuestas, dict_label_encoder, dict_encoder_riesgo_tratamiento2
# from utils.common import create_user_supabase, create_record_in_db, get_db
from utils.common import create_user_supabase
from expert_system import *
from models import Users

router = APIRouter(tags=['interface'])



load_dotenv()

target_col_cannabis_se = os.getenv("TARGET_COL_CANNABIS_SE")
target_col_psilocibina_se = os.getenv("TARGET_COL_PSILOCIBINA_SE")
target_col_cannabis_gb = os.getenv("TARGET_COL_CANNABIS_GB")
target_col_psilocibina_gb = os.getenv("TARGET_COL_PSILOCIBINA_GB")

model_cannabis = os.getenv("MODEL_CANNABIS_PATH")
model_psilocibina = os.getenv("MODEL_PSILOCIBINA_PATH")

# Cargar los modelos
model_cannabis = load_model(model_cannabis)
model_psilocibina = load_model(model_psilocibina)


@router.post("/predict-external-risk",
            summary="Predice el riesgo de un tratamiento psicoterapéutico con cannabis y psilocibina")
def predict_external_risk(request: UserData):
    
    try:
        # TODO: eventualmente, si el usuario ya existe retornar una excepción, y en la interfaz poner un botón para sobreescribir el usuario o cancelar la solicitud
        # ^poner en lower() el nombre del usuario 
        """
        # Comprueba si el usuario ya existe en la base de datos
        existing_user = db.query(exists().where(Users.nombre == request.nombre)).scalar()

        if existing_user:
            print(f'El usuario {request.nombre} ya existe en la base de datos.')
            raise HTTPException(status_code=409, detail="El usuario ya existe en la base de datos")
        """
        # Obtener los datos de prueba recibidos en la solicitud a la API y convertirlos en un DataFrame
        user_data = request.model_dump()

        # Convertir el diccionario a un DataFrame
        df_test = pd.DataFrame([user_data], columns=user_data.keys())

        # Renombrar columnas del DF externo para match las columnas del modelo 
        df_test.rename(columns=dict_rename_external_columns, inplace=True)
        
        # DF no codificado, unicamente con las columnas que se van a utilizar para hacer la prediccion
        df_prediction = df_test[prediction_columns].copy()

        # Reemplazar valores nulos por 'Sin Dato'
        if df_prediction.isnull().values.any():
            df_prediction.fillna('Sin Dato', inplace=True)
        df_prediction.replace({'N/A': 'Sin Dato'}, inplace=True)
        
        # Codificar las variables con multiples respuestas
        df_prediction, df_prediction_combined, df_prediction_encoded = get_one_hot_encoding(df_prediction)
        
        # Transformar los datos a valores booleanos y renombrar columnas necesarias
        df_prediction_combined = transform_data(df_prediction_combined, dict_renombrar_respuestas)
        df_prediction_encoded = transform_data(df_prediction_encoded, dict_renombrar_respuestas)

        df_prediction_encoded = get_label_encoding(df_prediction_encoded, dict_label_encoder)
        df_prediction_encoded = pd.get_dummies(df_prediction_encoded)

        # Dividir dataset según la sustancia
        df_prediction_encoded_cannabis, df_prediction_encoded_psilocibina = divide_dataset(df_prediction_encoded)


        df_prediction_encoded_cannabis = setup_test_data(df_prediction_encoded_cannabis, model_cannabis)
        df_prediction_encoded_psilocibina = setup_test_data(df_prediction_encoded_psilocibina, model_psilocibina)

        # Hacer predicciones con el GB
        df_prediction_encoded_cannabis[target_col_cannabis_gb] = model_cannabis.predict(df_prediction_encoded_cannabis)
        df_prediction_encoded_psilocibina[target_col_psilocibina_gb] = model_psilocibina.predict(df_prediction_encoded_psilocibina)
        
        # Invertir el diccionario para mapear valores numéricos a texto
        dict_decoder_riesgo_tres_niveles = {v: k for k, v in dict_encoder_riesgo_tratamiento2["tres_niveles"].items()}
        
        # Agregar el resultado en texto al DF con los datos de ambas sustancias
        df_prediction_combined[target_col_cannabis_gb] = df_prediction_encoded_cannabis[target_col_cannabis_gb].map(dict_decoder_riesgo_tres_niveles)
        df_prediction_combined[target_col_psilocibina_gb] = df_prediction_encoded_psilocibina[target_col_psilocibina_gb].map(dict_decoder_riesgo_tres_niveles)
                
        # Ejecutar el sistema experto
        execute_expert_system(df_prediction_combined, df_prediction_encoded_cannabis, target_col_cannabis_se)
        execute_expert_system(df_prediction_combined, df_prediction_encoded_psilocibina, target_col_psilocibina_se)
        
        # Codificar el nivel de riesgo 
        df_prediction_encoded_cannabis = encode_column(df_prediction_encoded_cannabis, target_col_cannabis_se, dict_encoder_riesgo_tratamiento2["cuatro_niveles"])
        df_prediction_encoded_psilocibina = encode_column(df_prediction_encoded_psilocibina, target_col_psilocibina_se, dict_encoder_riesgo_tratamiento2["cuatro_niveles"])

        df_prediction_combined[target_col_cannabis_gb] = df_prediction_encoded_cannabis.get(target_col_cannabis_gb, pd.Series()).map(dict_decoder_riesgo_tres_niveles).fillna("Desconocido")
        df_prediction_combined[target_col_psilocibina_gb] = df_prediction_encoded_psilocibina.get(target_col_psilocibina_gb, pd.Series()).map(dict_decoder_riesgo_tres_niveles).fillna("Desconocido")

        # Convertir a diccionario
        final_results = df_prediction_combined.to_dict(orient="records")
        
        # Guarda los datos en la base de datos
        user_data["riesgo_cannabis_se"] = final_results[0][target_col_cannabis_se]
        user_data["riesgo_cannabis_gb"] = final_results[0][target_col_cannabis_gb]

        user_data["riesgo_psilocibina_se"] = final_results[0][target_col_psilocibina_se]
        user_data["riesgo_psilocibina_gb"] = final_results[0][target_col_psilocibina_gb]
        
        # print("user_data:", user_data)
        # db = get_db()
        # create_record_in_db(Users, user_data, db)
        # TODO: aca poner la opcion para hacerlo en local con create record db pero buscar si se puede hacer con psycopg2
        # TODO: y hacer tbn que corra con el backend en local
        create_user_supabase(user_data)

    
    except Exception as e:
        print(f'Exception: {e}')
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail=str(e))   

    else:
        return final_results



# @router.get("/home")
# def home():
#     return {'API de Predicción de Riesgo para un Tratamiento Psicoterapéutico con Cannabis y Psilocibina.'}

