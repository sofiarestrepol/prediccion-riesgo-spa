import pandas as pd
from services.dataframe_service import rename_cols
from definitions import columnas_categoricas, cols_dependencia_abuso, dict_cols_binarias

# TODO: Generalizar, enviar cols cat como argumento
def get_one_hot_encoding(df):
    df_encoded = df.copy()
    for col in columnas_categoricas:
        # Reemplazar valores faltantes con un valor por defecto y asegurarse que sean listas de Python
        df_encoded[col] = df_encoded[col].apply(
            lambda x: x if isinstance(x, list) else [x] if pd.notnull(x) else []
        )
    # Crear columnas binarias usando 'explode' para descomponer las listas en filas
    for col in columnas_categoricas:
        df_encoded = df_encoded.explode(col)

    # Aplica One-Hot Encoding a las columnas categóricas del DF con los datos explotados
    df_encoded = pd.get_dummies(df_encoded, columns=columnas_categoricas, prefix=columnas_categoricas)
    # Agrupar por el índice original para reconstruir el DataFrame en la forma deseada
    df_encoded = df_encoded.groupby(df_encoded.index).max().reset_index(drop=True)

    df_combined = df_encoded.copy()

    return df, df_combined, df_encoded


# TODO: generalizar. enviar como arg las columnas y el dict de mapeo
# TODO: optimizar ?
# TODO; pasar a utils
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


def get_label_encoding(df, dict_label_encoder):
    # Realizar codificación con Label Encoding para variables seleccionadas
    cols_label_encoder = [col for col in df.columns if 'Frecuencia' in col]

    for col in cols_label_encoder:
        df[col] = df[col].replace("Cada año o menos de una vez al año", "Cada año")

        # Codificación Frecuencia de Consumo
        df[col] = df[col].replace(dict_label_encoder['frecuencia'])
        df[col] = df[col].astype(int)

    # Codificación Cantidad de Sesiones con Macrodosis
    df['Sesiones Macrodosis'] = df['Sesiones Macrodosis'].map(dict_label_encoder["sesiones_macro"])
    df['Sesiones Macrodosis'] = df['Sesiones Macrodosis'].astype(int)

    # Codificación Cantidad de Tratamientos con SPA
    df['Cantidad Tratamientos'] = df['Cantidad Tratamientos'].map(dict_label_encoder["cantidad_tratamientos"])
    df['Cantidad Tratamientos'] = df['Cantidad Tratamientos'].astype(int)

    return df