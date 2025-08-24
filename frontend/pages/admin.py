import json
import streamlit as st
import pandas as pd
import numpy as np
from pprint import pprint

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from frontend.utils.common import load_data


st.page_link("app.py", label="Formulario de Riesgo")
st.set_page_config(page_title="Panel de Administración", layout="wide", initial_sidebar_state="collapsed", page_icon="👨‍💻"  )

st.title("Panel de Administración")


if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    user = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    with open('frontend/config/admins.json', 'r') as f:
        data = json.load(f)
    admins = data["admins"]

    if st.button("Ingresar"):
        for admin in admins:
            if admin["username"] == user and admin["password"] == password:
                st.session_state["logged_in"] = True
                st.success("Login exitoso")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
else:
    st.subheader("Dashboard de Usuarios")

    try:
        df = load_data()

        # Filtros
        st.sidebar.header("Filtros")
        nombre_filtro = st.sidebar.text_input("Buscar por nombre")
        riesgo_filtro = st.sidebar.selectbox("Filtrar por nivel de riesgo", ["Todos"] + df["riesgo_cannabis_se"].unique().tolist())

        df_filtrado = df.copy()
        df_filtrado = df_filtrado.astype(str).drop_duplicates(subset=[c for c in df_filtrado.columns if c != "id"])


        if nombre_filtro:
            df_filtrado = df_filtrado[df_filtrado["nombre"].str.contains(nombre_filtro, case=False)]
        if riesgo_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado["riesgo_cannabis_se"] == riesgo_filtro]

        st.dataframe(df_filtrado, use_container_width=True)

        # Botón para descargar
        # csv = df_filtrado.to_csv(index=False).encode("utf-8")
        # st.download_button("⬇️ Descargar CSV", data=csv, file_name="usuarios_filtrados.csv", mime="text/csv")

    except Exception as e:
        st.error("Error al cargar los datos")
        st.error(str(e))
