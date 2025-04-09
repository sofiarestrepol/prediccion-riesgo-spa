import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
import pandas as pd

from expert_system import *
from definitions import *


def rename_cols(df, dict_mapeo):
    # Renombrar las columnas para tener mas claridad y facil acceso
    df.rename(columns=dict_mapeo, inplace=True)


# Realizar el preprocesamiento de los datos de prueba
def delete_columns(df):
    for col in df.columns:
        if col in columns_to_drop:
            df.drop(columns=[col], inplace=True)


def preprocess_data(df):
    # Elimina columnas innecesarias para el modelo
    delete_columns(df)

    # Verificar si hay valores nulos y en caso tal reemplazarlos por 'Sin Dato'
    if df.isnull().values.any():
        df.fillna('Sin Dato', inplace=True)

    df.replace({'N/A': 'Sin Dato'}, inplace=True)



def get_one_hot_encoding(df):
    # Separar las opciones de respuesta para cada una de las columnas categóricas y generar una lista con las respuestas
    for col in columnas_categoricas:
        df[col] = df[col].str.split(';')  
    # Crear columnas binarias usando 'explode' para descomponer las listas en filas
    for col in columnas_categoricas:
        df = df.explode(col)
    # Aplicar One-Hot Encoding a las columnas categóricas del DF con los datos explotados
    df_encoded = pd.get_dummies(df, columns=columnas_categoricas, prefix=columnas_categoricas)
    # Agrupar por el índice original para reconstruir el DataFrame en la forma deseada
    df_encoded = df_encoded.groupby(df_encoded.index).max().reset_index(drop=True)

    df = df_encoded.copy()

    return df_encoded, df

    

def transform_to_bool(df):
    # Renombrar columnas en texto a valores binarios
    for col in cols_dependencia_abuso:
        df[col] = df[col].map(dict_cols_binarias)

    # Convertir las columnas binarias (1,0) en booleanas (True, False)
    for col in cols_dependencia_abuso:
        df[col] = df[col].astype(bool)



def transform_data(df, dict_mapeo):
    try:
        # Transformar los datos a valores booleanos
        transform_to_bool(df)
        # Renombrar columnas necesarias
        rename_cols(df, dict_mapeo)
        
        # Reemplazar caracteres especiales en los nombres de las columnas
        df.columns = df.columns.str.replace(r'[^\w\s/,\']', '_', regex=True)


    except Exception as e:
        print(f'Ocurrió un error en el preprocesamiento de los datos: {e}')

    else:
        return df
    


def get_label_encoding(df_test_encoded):
    # Realizar codificación con Label Encoding para variables seleccionadas
    cols_label_encoder = [col for col in df_test_encoded.columns if 'Frecuencia' in col]

    for col in cols_label_encoder:
        df_test_encoded[col] = df_test_encoded[col].replace("Cada año o menos de una vez al año", "Cada año")

        # Codificación Frecuencia de Consumo
        df_test_encoded[col] = df_test_encoded[col].replace(dict_encoder_frecuencia)
        df_test_encoded[col] = df_test_encoded[col].astype(int)

    # Codificación Cantidad de Sesiones con Macrodosis
    df_test_encoded['Sesiones Macrodosis'] = df_test_encoded['Sesiones Macrodosis'].map(dict_encoder_sesiones_macro)
    df_test_encoded['Sesiones Macrodosis'] = df_test_encoded['Sesiones Macrodosis'].astype(int)

    # Codificación Cantidad de Tratamientos con SPA
    df_test_encoded['Cantidad Tratamientos'] = df_test_encoded['Cantidad Tratamientos'].map(dict_encoder_cantidad_tratamientos)
    df_test_encoded['Cantidad Tratamientos'] = df_test_encoded['Cantidad Tratamientos'].astype(int)



def divide_dataset(df_test_encoded):
    # Generar un DF para cada sustancia
    df_test_encoded_cannabis = df_test_encoded.copy()
    df_test_encoded_psilocibina = df_test_encoded.copy()

    for col in df_test_encoded_cannabis.columns:
        if 'Psilocibina' in col or 'Otros' in col or 'Sin Dato' in col or 'Tipo de Dosis' in col or 'Sin Razón' in col:
            df_test_encoded_cannabis.drop(columns=[col], inplace=True)


    for col in df_test_encoded_psilocibina.columns:
        if 'Cannabis' in col or 'Otros' in col or 'Sin Dato' in col or 'Sin Razón' in col:
            df_test_encoded_psilocibina.drop(columns=[col], inplace=True)

    return df_test_encoded_cannabis, df_test_encoded_psilocibina



def setup_test_data(df, model):

    # Obtener los nombres de las características con las que se entrenó el modelo
    features_model = model.feature_names_in_
    # Definir la variable objetivo y las columnas de entrada
    # features = [col for col in df.columns if col != target]  # Excluir la variable objetivo

    # Asegurar que las columnas numéricas sean float/int
    # df[features] = df[features].apply(pd.to_numeric, errors="coerce").fillna(False)

    # Crear un DataFrame vacío con las columnas esperadas
    df_model = pd.DataFrame(columns=features_model)

    # Unir con el DataFrame de prueba, asegurando que las columnas coincidan
    df_model = pd.concat([df_model, df], ignore_index=True)

    # # Ordenar las columnas para que coincidan con el modelo
    df_model = df_model[features_model]

    preprocess_data(df_model)
    rename_cols(df_model, dict_renombrar_respuestas)
    # Reemplazar caracteres especiales en los nombres de las columnas
    df_model.columns = df_model.columns.str.replace(r'[^\w\s/,\']', '_', regex=True)
    df_model.replace({'Sin Dato': False}, inplace=True)
    
    return df_model



def execute_expert_system(df_test, df_test_encoded, target_col):
    try: 
        # Definir el conjunto de reglas según la sustancia
        if 'Cannabis' in target_col:
            riesgo_bajo = get_low_risk_cannabis(df_test)
            riesgo_medio = get_medium_risk_cannabis(df_test)
            riesgo_alto = get_high_risk_cannabis(df_test)

        elif 'Psilocibina' in target_col:
            riesgo_bajo = get_low_risk_psilocibina(df_test)
            riesgo_medio = get_medium_risk_psilocibina(df_test)
            riesgo_alto = get_high_risk_psilocibina(df_test)

        # Inicializar la nueva variable con 'Riesgo Desconocido'
        df_test_encoded[target_col] = 'Riesgo Desconocido'
        df_test[target_col] = 'Riesgo Desconocido'

        # Asignar un nivel de riesgo bajo a los casos que lo cumplan
        df_test_encoded.loc[riesgo_bajo, target_col] = 'Riesgo Bajo'
        df_test.loc[riesgo_bajo, target_col] = 'Riesgo Bajo'

        # Asignar el nivel de riesgo medio a los casos que lo cumplan y que no tengan un valor de riesgo asociado
        df_test_encoded.loc[(df_test_encoded[target_col] == 'Riesgo Desconocido') & riesgo_medio, 
                    target_col] = 'Riesgo Medio'
        df_test.loc[(df_test[target_col] == 'Riesgo Desconocido') & riesgo_medio, 
                    target_col] = 'Riesgo Medio'

        # Se añade el nivel de riesgo alto a los casos que lo cumplan y que no tengan un valor de riesgo asociado
        df_test_encoded.loc[(df_test_encoded[target_col] == 'Riesgo Desconocido') & riesgo_alto, 
                    target_col] = 'Riesgo Alto'
        df_test.loc[(df_test[target_col] == 'Riesgo Desconocido') & riesgo_alto, 
                    target_col] = 'Riesgo Alto'
        
    except Exception as e:
        print(f'Ocurrió un error en la ejecución del sistema experto: {e}')



def encode_risk_level(df_test_encoded, target_col):
    # Codificación del Nivel de Riesgo del Tratamiento 
    df_test_encoded[target_col] = df_test_encoded[target_col].map(dict_encoder_riesgo_tratamiento)



def filter_df(df_encoded, target_col):
    # Eliminar filas donde la clase objetivo tiene solo un miembro
    df_encoded_filtrado = df_encoded[df_encoded[target_col] != 0]
    return df_encoded_filtrado



