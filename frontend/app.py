# streamlit run app.py
import streamlit as st
import requests
from definitions import *
from pprint import pprint

from config import DATABASE_CONFIG


st.title("Predicción del Nivel de Riesgo para un Tratamiento Psicoterapéutico con Cannabis y Psilocibina")


st.write('Formulario para evaluar al usuario y predecir su nivel de riesgo según su perfil biológico y comportamental.')

# Datos del usuario
st.header("Datos del Usuario")
autorizacion = st.checkbox("Autorización para el uso de los datos para el entrenamiento de un modelo de IA con fines investigativos.")
nombre = st.text_input("Nombre y apellidos del usuario")
edad = st.number_input("Edad", min_value=18, max_value=120)
sexo = st.selectbox("Sexo Biológico", ["Masculino", "Femenino", "Otro"])

# Datos clínicos (Historial y Condiciones Médicas)
st.header("Datos Clínicos")
st.subheader("Historial Familiar", divider='grey', help='Seleccionar las condiciones relevantes presentes en la familia del usuario')
historial_familiar = st.pills(
    'Selecciona las condiciones médicas relevantes presentes en la familia del usuario',  options["historial_familiar"],
    selection_mode="multi")

st.subheader("Condiciones Médicas", divider='grey', help='Seleccionar las condiciones relevantes presentes en el usuario')
condiciones_medicas = st.pills(
    'Selecciona las condiciones médicas relevantes presentes en el usuario', options["condiciones_medicas"],
    selection_mode="multi")


# Datos de consumo de sustancias
st.header("Consumo de Sustancias")

st.subheader("Consumo de Cannabis")
frecuencia_cannabis = st.radio(
    'Frecuencia de consumo de cannabis', 
    options["frecuencia"],
    index=None)

proposito_cannabis = st.radio(
    'Propósito del consumo de cannabis', 
    options["propósito"],
    index=None)

dependencia_cannabis = st.pills(
    '¿Ha experimentado dependencia al cannabis?', 
    options["bool"],
    key="dependencia_cannabis")

abuso_cannabis = st.pills(
    '¿Ha abusado del cannabis?', 
    options["bool"],
    key="abuso_cannabis")


# st.markdown('Efectos **Positivos** con el Cannabis')
efectos_positivos_cannabis = st.pills(
    'Efectos POSITIVOS con el cannabis', 
    options_cannabis["efectos_positivos"],
    selection_mode="multi")

# st.markdown('Efectos **Negativos** con el Cannabis')
efectos_negativos_cannabis = st.pills(
    'Efectos NEGATIVOS con el cannabis', 
    options_cannabis["efectos_negativos"],
    selection_mode="multi")


# Consumo de Psilocibina
st.subheader("Consumo de Psilocibina")
frecuencia_psilocibina = st.radio(
    'Frecuencia de consumo de psilocibina', 
    options["frecuencia"],
    index=None)

proposito_psilocibina = st.radio(
    'Propósito del consumo de psilocibina', 
    options["propósito"],
    index=None)

dependencia_psilocibina = st.pills(
    '¿Ha experimentado dependencia a la psilocibina?', 
    options["bool"],
    key="dependencia_psilocibina")

abuso_psilocibina = st.pills(
    '¿Ha abusado de la psilocibina?', 
    options["bool"],
    key="abuso_psilocibina")


efectos_positivos_psilocibina = st.pills(
    'Efectos POSITIVOS con la psilocibina', 
    options_psilocibina["efectos_positivos"],
    selection_mode="multi")

efectos_negativos_psilocibina = st.pills(
    'Efectos NEGATIVOS con la psilocibina', 
    options_psilocibina["efectos_negativos"],
    selection_mode="multi")


st.header('Tratamientos Previos con Sustancias') 

# TODO: tratamiento con cannabis. if ha realizado trat con cannabis... else, continua a la sgte seccion
# TODO: if no ha realizado tratamiento con ninguna, se elimina la seccion y las respuestas son N/A
sustancia_previa = st.radio(
    'Sustancias utilizadas en tratamientos previos', 
    options_tratamiento["sustancia_previa"],
    index=None)

cantidad_tratamientos_previos = st.radio(
    'Cantidad de tratamientos previos con sustancias psicoactivas',
    options_tratamiento["cantidad_tratamientos_previos"],
    index=None)

tipo_dosis = st.radio(
    'Tipo de dosis utilizada en tratamientos previos',
    options_tratamiento["tipo_dosis"],
    index=None)


cantidad_tratamientos_macro = st.radio(
    'Cantidad de sesiones de macrodosis en tratamientos previos',
    options_tratamiento["cantidad_sesiones_macro"],
    index=None)

calificacion_tratamientos_previos = st.slider(
    'Calificación de tratamientos previos', 
    min_value=1, 
    max_value=5, 
    step=1)

comentario = st.text_area(
    "Comentarios adicionales sobre el usuario o el tratamiento")

predecir = st.button("Predecir")



try:
    if predecir:

        # TODO: pasar campos obligatorios a definitions.py
        campos_obligatorios = {
            "historial_familiar": historial_familiar,
            "condiciones_medicas": condiciones_medicas,
            "frecuencia_cannabis": frecuencia_cannabis,
            "frecuencia_psilocibina": frecuencia_psilocibina,
            "proposito_cannabis": proposito_cannabis,
            "proposito_psilocibina": proposito_psilocibina,
            "dependencia_cannabis": dependencia_cannabis,
            "dependencia_psilocibina": dependencia_psilocibina,
            "abuso_cannabis": abuso_cannabis,
            "abuso_psilocibina": abuso_psilocibina,
            "efectos_positivos_cannabis": efectos_positivos_cannabis,
            "efectos_negativos_cannabis": efectos_negativos_cannabis,
            "efectos_positivos_psilocibina": efectos_positivos_psilocibina,
            "efectos_negativos_psilocibina": efectos_negativos_psilocibina,
            "sustancia_previa": sustancia_previa,
            "cantidad_tratamientos_previos": cantidad_tratamientos_previos,
            "tipo_dosis": tipo_dosis,
            "cantidad_tratamientos_macro": cantidad_tratamientos_macro,
        }

        campos_faltantes = [campo for campo, valor in campos_obligatorios.items() if valor in [None, '', []]]

        if campos_faltantes:
            campos_faltantes = [campo.replace('_', ' ').title() for campo in campos_faltantes]
            st.warning(f"Por favor completa todos los campos obligatorios antes de predecir: {', '.join(campos_faltantes)}")
        
        else:
            payload = {
                "autorizacion": autorizacion,
                "nombre": nombre,
                "edad": edad,
                "sexo": sexo,
                "historial_familiar": historial_familiar,
                "condiciones_medicas": condiciones_medicas,
                "frecuencia_cannabis": frecuencia_cannabis,
                "frecuencia_psilocibina": frecuencia_psilocibina,
                "proposito_cannabis": proposito_cannabis,
                "proposito_psilocibina": proposito_psilocibina,
                "dependencia_cannabis": dependencia_cannabis,
                "dependencia_psilocibina": dependencia_psilocibina,
                "abuso_cannabis": abuso_cannabis,
                "abuso_psilocibina": abuso_psilocibina,
                "efectos_positivos_cannabis": efectos_positivos_cannabis,
                "efectos_negativos_cannabis": efectos_negativos_cannabis,
                "efectos_positivos_psilocibina": efectos_positivos_psilocibina,
                "efectos_negativos_psilocibina": efectos_negativos_psilocibina,
                "sustancia_previa": sustancia_previa,
                "cantidad_tratamientos_previos": cantidad_tratamientos_previos,
                "tipo_dosis": tipo_dosis,
                "cantidad_tratamientos_macro": cantidad_tratamientos_macro,
                "calificacion_tratamientos_previos": calificacion_tratamientos_previos,
                "comentario": comentario
            }

            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }

            response = requests.post(DATABASE_CONFIG['PREDICT_EXTERNAL_RISK_URL'], json=payload, headers=headers, timeout=180)
            # response = requests.post("http://localhost:8000/predict-external-risk/", json=payload, headers=headers, timeout=180)

            # st.text(f"Status code: {response.status_code}")
            # st.json(response.json())  
            
            if response.status_code == 200:
                st.success(f"Tu respuesta ha sido registrada exitosamente.")
                dict_riesgo = {}
                riesgo_cannabis = 'Riesgo Desconocido'
                
                response = response.json()[0]
            
                response_cannabis_gb = response["Nivel de Riesgo Tratamiento Cannabis (GB)"]
                response_cannabis_se = response["Nivel de Riesgo Tratamiento Cannabis (SE)"]
                response_psilocibina_gb = response["Nivel de Riesgo Tratamiento Psilocibina (GB)"]
                response_psilocibina_se = response["Nivel de Riesgo Tratamiento Psilocibina (SE)"]

                if response_cannabis_gb == response_cannabis_se:
                    riesgo_cannabis = response_cannabis_gb

                # TODO: poner los dos si son diferentes o validar cual de los dos se acerca mas al caso
                else:
                    if response_cannabis_gb != 'Riesgo Desconocido':
                        riesgo_cannabis = response_cannabis_gb 
                    elif response_cannabis_gb == 'Riesgo Desconocido' and response_cannabis_se != 'Riesgo Desconocido':
                        riesgo_cannabis = response_cannabis_se

                if response_psilocibina_gb == response_psilocibina_se:
                    riesgo_psilocibina = response_psilocibina_gb

                else:
                    if response_psilocibina_gb != 'Riesgo Desconocido':
                        riesgo_psilocibina = response_psilocibina_gb 
                    elif response_psilocibina_gb == 'Riesgo Desconocido' and response_psilocibina_se != 'Riesgo Desconocido':
                        riesgo_psilocibina = response_cannabis_se

                
                dict_riesgo = {
                    "Riesgo Cannabis": riesgo_cannabis,
                    "Riesgo Psilocibina": riesgo_psilocibina
                    
                }
                # st.success(f"Riesgo Cannabis: {riesgo_cannabis}")
                # st.success(f"Riesgo Psilocibina: {riesgo_psilocibina}")
            
            else:
                st.error(f"Error en la predicción: {response.status_code}")


    # st.divider()
    # st.login() # Eventualmente, auth para que los usuarios autorizados puedan ver el resultado de la prediccion

except requests.exceptions.Timeout:
    st.error("La solicitud tomó demasiado tiempo. Intenta de nuevo más tarde.")

except requests.exceptions.ConnectionError:
    st.error("No se pudo conectar al servidor.")

except requests.exceptions.RequestException as e:
    st.error("Error inesperado al hacer la solicitud.")
    st.error(str(e))



