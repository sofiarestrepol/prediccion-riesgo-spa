import pandas as pd
import numpy as np
from joblib import load
from pydantic import BaseModel, ValidationError
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import traceback
import os

from expert_system import * 
from utils import *
from test_data import *
from definitions import columnas_df

# Cargar variables de entorno
load_dotenv()
random_state_cannabis = int(os.getenv("RANDOM_STATE_CANNABIS"))
random_state_psilocibina = int(os.getenv("RANDOM_STATE_PSILOCIBINA"))

target_col_cannabis_se = os.getenv("TARGET_COL_CANNABIS_SE")
target_col_psilocibina_se = os.getenv("TARGET_COL_PSILOCIBINA_SE")
target_col_cannabis_gb = os.getenv("TARGET_COL_CANNABIS_GB")
target_col_psilocibina_gb = os.getenv("TARGET_COL_PSILOCIBINA_GB")


pd.set_option('future.no_silent_downcasting', True)


try:
    model_psilocibina = load('../models/best_model_psilocibina.joblib')
    model_cannabis = load('../models/best_model_cannabis.joblib')
    print('Los datos se cargaron correctamente')

except Exception as e:
    print(f'Ocurrió un error en la carga de los datos: {e}')


# Crear aplicación FastAPI
app = FastAPI()

@app.get("/predict-survey-risk")
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


@app.get("/predict-individual-risk")
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



# Definir el formato de los datos a predecir
class DataPredict(BaseModel):
    data_to_predict: list[list] = [sujeto7]


@app.post("/predict-external-risk")
def predict_external_risk(request: DataPredict):
    """
    Predice el nivel de riesgo para un tratamiento con sustancias psicoactivas según el perfil del paciente.

    - Frecuencia de Consumo de Psilocibina
    - Frecuencia de Consumo de Cannabis
    - Propósito del Consumo de Cannabis
    - Propósito del Consumo de Psilocibina
    - Dependencia al Cannabis
    - Dependencia a la Psilocibina
    - Consumo Abusivo de Cannabis
    - Consumo Abusivo de Psilocibina
    - Cantidad de Tratamientos con Psilocibina
    - Tipo de Dosis de Psilocibina
    - Cantidad de Sesiones de Macrodosis con Psilocibina
    - Calificación del Tratamiento
    - Historial Familiar
    - Condiciones Medicas
    - Efectos Positivos Cannabis
    - Efectos Negativos Cannabis
    - Efectos Positivos Psilocibina
    - Efectos Negativos Psilocibina
    
    Las preguntas de 'Frecuencia de Consumo' permiten las siguientes opciones de respuesta: 
    - Diario, Varias veces a la semana, Cada semana, Varias veces al mes, Cada mes, Varias veces al año, Cada año.

    Las preguntas de 'Propósito del Consumo' determinan con qué finalidad se consumió la sustancia, y permiten las siguientes opciones de respuesta:
    - Fines recreativos, Fines terapéuticos, Ambos.

    Las preguntas de 'Dependencia' y 'Consumo Abusivo' definen si el paciente ha experimentado dependencia a la sustancia y si ha abusado de ella respectivamente, y sus respuestas tienen formato de 'Si' o 'No'.

    La 'Cantidad de Tratamientos' se refiere a cuántos tratamientos con psilocibina ha realizado el paciente previamente. Las opciones de respuesta validas son:
    - Uno, Dos, Más de tres, y N/A en caso de no haber realizado tratamientos previos.

    'Tipo de Dosis' representa la dosificación utilizada para el consumo de psilocibina del paciente. Permite las siguientes opciones:
    - Microdosis, Macrodosis, Ambas.

    La pregunta 'Cantidad de Sesiones de Macrodosis' hace referencia a cuántas sesiones de macrodosis ha realizado el paciente con psilocibina. Las posibles opciones de respuesta son:
    - Una sesión de un día, 1-5 sesiones de un día, Más de 10 sesiones de un día, Otros
    
    La 'Calificación del Tratamiento' define un valor entre 1 y 5 que el paciente otorga a los tratamientos previos que haya realizado con alguna de las sustancias psicoactivas.    

    Los campos 'Condiciones Medicas' e 'Historial Familiar' lista los trastornos significativos que presente el participante y aquellos que presente un miembro de su familia respectivamente. 

    Las preguntas de 'Efectos Positivos' y 'Efectos Negativos' listan los efectos que haya experimentado el paciente con cada una de las sustancias.
        
    Todas los campos permiten la opción 'N/A' como respuesta en caso de que la pregunta no aplique para el paciente.

    """
    try:
        # Obtener los datos de prueba recibidos en la solicitud a la API y convertirlos en un DataFrame
        list_data = request.data_to_predict
        df_test = pd.DataFrame(list_data, columns=columnas_df)

        rename_cols(df_test, dict_rename_original_columns)
        
        # Realizar el preprocesamiento de los datos de prueba
        preprocess_data(df_test)

        # Codificar las variables con multiples respuestas
        df_test_encoded, df_test = get_one_hot_encoding(df_test)
        
        # Realizar transformaciones necesarias a los datos de prueba
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

        # Preparar datos para la predicción
        df_model_cannabis = setup_test_data(df_test_encoded_cannabis, model_cannabis)
        df_model_psilocibina = setup_test_data(df_test_encoded_psilocibina, model_psilocibina)

        # Realizar predicción
        df_test_encoded_cannabis[target_col_cannabis_gb] = model_cannabis.predict(df_model_cannabis)
        df_test_encoded_psilocibina[target_col_psilocibina_gb] = model_psilocibina.predict(df_model_psilocibina)

        # Mapear valores numéricos a texto
        dict_decoder_riesgo_tres_niveles = {v: k for k, v in dict_encoder_riesgo_tres_niveles.items()}

        df_test[target_col_cannabis_gb] = df_test_encoded_cannabis.get(target_col_cannabis_gb, pd.Series()).map(dict_decoder_riesgo_tres_niveles).fillna("Desconocido")
        df_test[target_col_psilocibina_gb] = df_test_encoded_psilocibina.get(target_col_psilocibina_gb, pd.Series()).map(dict_decoder_riesgo_tres_niveles).fillna("Desconocido")

        # Convertir a diccionario
        dict_data = df_test.to_dict(orient="records")

        return {
            "Riesgo Cannabis": {
                "Predicción Sistema Experto": dict_data[0]['Nivel de Riesgo Tratamiento Cannabis (SE)'],
                "Predicción Modelo Gradient Boosting": dict_data[0]['Nivel de Riesgo Tratamiento Cannabis (GB)'],
            },
            "Riesgo Psilocibina": {
                "Predicción Sistema Experto": dict_data[0]['Nivel de Riesgo Tratamiento Psilocibina (SE)'],
                "Predicción Modelo Gradient Boosting": dict_data[0]['Nivel de Riesgo Tratamiento Psilocibina (GB)'],
            }
        }
    
    except Exception as e:
        print(f'Exception: {e}')
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail=str(e))    



# @app.get("/home")
# def home():
#     return {'API de Predicción de Riesgo para un Tratamiento Psicoterapéutico con Cannabis y Psilocibina.'}
