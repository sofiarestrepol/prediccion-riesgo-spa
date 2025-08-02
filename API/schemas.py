from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from test_data import *
import uuid


class DataPredict(BaseModel):
    data_to_predict: list[list] = [sujeto7]


class UserData(BaseModel):
    autorizacion: bool
    # fecha: Optional[datetime] = None
    nombre: str
    edad: int
    sexo: str
    historial_familiar: list
    condiciones_medicas: list
    frecuencia_cannabis: str
    frecuencia_psilocibina: str
    proposito_cannabis: str
    proposito_psilocibina: str
    dependencia_cannabis: str
    dependencia_psilocibina: str
    abuso_cannabis: str
    abuso_psilocibina: str
    efectos_positivos_cannabis: list
    efectos_negativos_cannabis: list
    efectos_positivos_psilocibina: list
    efectos_negativos_psilocibina: list
    sustancia_previa: str
    cantidad_tratamientos_previos: str
    tipo_dosis: str
    cantidad_tratamientos_macro: str
    calificacion_tratamientos_previos: int
    comentario: str

    class Config:

        json_schema_extra = {
            'example': {
                'autorizacion': True,
                'nombre': 'Jane Doe',
                'edad': 25,
                'sexo': 'Femenino',
                'historial_familiar': ['Trastorno de Ansiedad Generalizada (TAG)',
                'Trastorno Depresivo Mayor o Persistente',
                'Adicción al alcohol'],
                'condiciones_medicas': ['Trastorno de Ansiedad Generalizada (TAG)'],
                'frecuencia_cannabis': 'Varias veces al mes',
                'frecuencia_psilocibina': 'Cada año o menos de una vez al año',
                'proposito_cannabis': 'Fines recreativos',
                'proposito_psilocibina': 'Fines terapéuticos',
                'dependencia_cannabis': 'No',
                'dependencia_psilocibina': 'No',
                'abuso_cannabis': 'Sí',
                'abuso_psilocibina': 'No',
                'efectos_positivos_cannabis': ['Aumento de creatividad',
                'Mejora en el estado de ánimo',
                'Reducción de inflamación o espasmos'],
                'efectos_negativos_cannabis': ['Aislamiento'],
                'efectos_positivos_psilocibina': ['Reducción de ansiedad',
                'Aumento de introspección',
                'Mayor sentido de propósito o satisfacción con la vida'],
                'efectos_negativos_psilocibina': ['No tuvo ningún efecto negativo'],
                'sustancia_previa': 'Psilocibina',
                'cantidad_tratamientos_previos': 'Dos',
                'tipo_dosis': 'Ambas',
                'cantidad_tratamientos_macro': 'Más de 10 sesiones de un día',
                'calificacion_tratamientos_previos': 5,
                'comentario': ''}
        }

