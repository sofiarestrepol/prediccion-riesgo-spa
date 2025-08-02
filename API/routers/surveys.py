import pandas as pd
import numpy as np
from joblib import load
from pydantic import BaseModel
from fastapi import HTTPException, APIRouter
from dotenv import load_dotenv
import traceback
import os
from expert_system import * 
from services.dataframe_service import *
from test_data import *
from definitions import columnas_df
from schemas import DataPredict

router = APIRouter(tags=['surveys'])

# Cargar variables de entorno
load_dotenv()
random_state_cannabis = int(os.getenv("RANDOM_STATE_CANNABIS"))
random_state_psilocibina = int(os.getenv("RANDOM_STATE_PSILOCIBINA"))

target_col_cannabis_se = os.getenv("TARGET_COL_CANNABIS_SE")
target_col_psilocibina_se = os.getenv("TARGET_COL_PSILOCIBINA_SE")
target_col_cannabis_gb = os.getenv("TARGET_COL_CANNABIS_GB")
target_col_psilocibina_gb = os.getenv("TARGET_COL_PSILOCIBINA_GB")


model_cannabis = os.getenv("MODEL_CANNABIS_PATH")
model_psilocibina = os.getenv("MODEL_PSILOCIBINA_PATH")




pd.set_option('future.no_silent_downcasting', True)


# Cargar los modelos
model_cannabis = load_model(model_cannabis)
model_psilocibina = load_model(model_psilocibina)

@router.get("/predict-survey-risk")
def predict_survey_risk():
    try:    
        df_test = pd.read_csv('../data/encuesta_test.csv')
        df_test.insert(0, "id", range(len(df_test)))
        rename_cols(df_test, dict_rename_original_columns)
        preprocess_data(df_test)
        df_test_encoded, df_test = get_one_hot_encoding(df_test)
        df_test = transform_data(df_test, dict_renombrar_respuestas)
        df_test_encoded = transform_data(df_test_encoded, dict_renombrar_respuestas)
        # Codificar con Label Encoding las variables con una gran cantidad de posibilidades de respuesta
        get_label_encoding(df_test_encoded)
        # Condificar con One Hot Encoding el resto de variables
        df_test_encoded = pd.get_dummies(df_test_encoded) 
        # Dividir el dataset de prueba según la sustancia
        df_test_encoded_cannabis, df_test_encoded_psilocibina = divide_dataset(df_test_encoded)
        # Ejecutar el sistema experto con los conjuntos de reglas para determinar el nivel de riesgo del individuo
        execute_expert_system(df_test, df_test_encoded_cannabis, target_col_cannabis_se)
        execute_expert_system(df_test, df_test_encoded_psilocibina, target_col_psilocibina_se)
        # Codificar el nivel de riesgo
        encode_risk_level(df_test_encoded_cannabis, target_col_cannabis_se)
        encode_risk_level(df_test_encoded_psilocibina, target_col_psilocibina_se)
        # Filtrar los datos de prueba para eliminar filas sin predicciones de riesgo
        df_test_encoded_cannabis = filter_df(df_test_encoded_cannabis, target_col_cannabis_se)
        df_test_encoded_psilocibina = filter_df(df_test_encoded_psilocibina, target_col_psilocibina_se)
        
        # hasta aca funciona
        df_model_cannabis = setup_test_data(df_test_encoded_cannabis, model_cannabis)
        df_model_psilocibina = setup_test_data(df_test_encoded_psilocibina, model_psilocibina)
        df_test_encoded_cannabis[target_col_cannabis_gb] = model_cannabis.predict(df_model_cannabis)
        df_test_encoded_psilocibina[target_col_psilocibina_gb] = model_psilocibina.predict(df_model_psilocibina)


        # Invertir el diccionario para mapear valores numéricos a texto
        dict_decoder_riesgo_tres_niveles = {v: k for k, v in dict_encoder_riesgo_tres_niveles.items()}

        df_test[target_col_cannabis_gb] = df_test_encoded_cannabis['Nivel de Riesgo Tratamiento Cannabis (GB)'].map(dict_decoder_riesgo_tres_niveles)
        df_test[target_col_psilocibina_gb] = df_test_encoded_psilocibina['Nivel de Riesgo Tratamiento Psilocibina (GB)'].map(dict_decoder_riesgo_tres_niveles)

        
        dict_data = df_test.to_dict(orient="records")


    except Exception as e:
        print(f'Exception: {e}')
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail=str(e))

    else:
        return dict_data


@router.get("/predict-individual-risk")
def predict_individual_risk(individual_id: int):
    try:    
        df_test = pd.read_csv('../data/encuesta_test.csv')
        df_test.insert(0, "id", range(len(df_test)))

        # individual = df_test[df_test["id"] == individual_id]  # Filtrar el DataFrame
        individual = df_test.loc[df_test["id"] == individual_id].copy()


        # Si el individuo no existe, lanzar una excepción
        if individual.empty:
            raise ValueError(f"El ID {individual_id} no existe en el dataset.")

        rename_cols(individual, dict_rename_original_columns)
        preprocess_data(individual)

        df_test_encoded, individual = get_one_hot_encoding(individual)
        individual = transform_data(individual, dict_renombrar_respuestas)
        df_test_encoded = transform_data(df_test_encoded, dict_renombrar_respuestas)

        # Codificar variables categóricas
        get_label_encoding(df_test_encoded)
        df_test_encoded = pd.get_dummies(df_test_encoded) 

        # Dividir dataset según la sustancia
        df_test_encoded_cannabis, df_test_encoded_psilocibina = divide_dataset(df_test_encoded)

        # Ejecutar el sistema experto
        execute_expert_system(individual, df_test_encoded_cannabis, target_col_cannabis_se)
        execute_expert_system(individual, df_test_encoded_psilocibina, target_col_psilocibina_se)

        # Codificar el nivel de riesgo
        encode_risk_level(df_test_encoded_cannabis, target_col_cannabis_se)
        encode_risk_level(df_test_encoded_psilocibina, target_col_psilocibina_se)

        # Filtrar filas sin predicciones de riesgo
        df_test_encoded_cannabis = filter_df(df_test_encoded_cannabis, target_col_cannabis_se)
        df_test_encoded_psilocibina = filter_df(df_test_encoded_psilocibina, target_col_psilocibina_se)

        # Preparar datos para la predicción
        df_model_cannabis = setup_test_data(df_test_encoded_cannabis, model_cannabis)
        df_model_psilocibina = setup_test_data(df_test_encoded_psilocibina, model_psilocibina)

        # Realizar predicción
        df_test_encoded_cannabis[target_col_cannabis_gb] = model_cannabis.predict(df_model_cannabis)
        df_test_encoded_psilocibina[target_col_psilocibina_gb] = model_psilocibina.predict(df_model_psilocibina)

        # Mapear valores numéricos a texto
        dict_decoder_riesgo_tres_niveles = {v: k for k, v in dict_encoder_riesgo_tres_niveles.items()}

        individual[target_col_cannabis_gb] = df_test_encoded_cannabis.get(target_col_cannabis_gb, pd.Series()).map(dict_decoder_riesgo_tres_niveles).fillna("Desconocido")
        individual[target_col_psilocibina_gb] = df_test_encoded_psilocibina.get(target_col_psilocibina_gb, pd.Series()).map(dict_decoder_riesgo_tres_niveles).fillna("Desconocido")

        # Convertir a diccionario
        dict_data = individual.to_dict(orient="records")



    except Exception as e:
        print(f'Exception: {e}')
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail=str(e))

    else:
        return {
            "Riesgo Cannabis": dict_data[0]['Nivel de Riesgo Tratamiento Cannabis (SE)'],
            "Riesgo Psilocibina": dict_data[0]['Nivel de Riesgo Tratamiento Psilocibina (SE)'],

            # "Riesgo Cannabis (SE)": dict_data[0]['Nivel de Riesgo Tratamiento Cannabis (SE)'],
            # "Riesgo Psilocibina (SE)": dict_data[0]['Nivel de Riesgo Tratamiento Psilocibina (SE)'],
            # "Riesgo Cannabis (GB)": dict_data[0]['Nivel de Riesgo Tratamiento Cannabis (GB)'],
            # "Riesgo Psilocibina (GB)": dict_data[0]['Nivel de Riesgo Tratamiento Psilocibina (GB)']
            }

        # return dict_data



