from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY, TIMESTAMP
from database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    autorizacion = Column(Boolean, nullable=False)
    # fecha = Column(TIMESTAMP(timezone=True))
    nombre = Column(String, nullable=False)
    edad = Column(Integer, nullable=False)
    sexo = Column(String, nullable=False)

    historial_familiar = Column(ARRAY(String), nullable=True)
    condiciones_medicas = Column(ARRAY(String), nullable=True)

    frecuencia_cannabis = Column(String, nullable=True)
    frecuencia_psilocibina = Column(String, nullable=True)

    proposito_cannabis = Column(String, nullable=True)
    proposito_psilocibina = Column(String, nullable=True)

    dependencia_cannabis = Column(String, nullable=True)
    dependencia_psilocibina = Column(String, nullable=True)

    abuso_cannabis = Column(String, nullable=True)
    abuso_psilocibina = Column(String, nullable=True)

    efectos_positivos_cannabis = Column(ARRAY(String), nullable=True)
    efectos_negativos_cannabis = Column(ARRAY(String), nullable=True)
    efectos_positivos_psilocibina = Column(ARRAY(String), nullable=True)
    efectos_negativos_psilocibina = Column(ARRAY(String), nullable=True)

    sustancia_previa = Column(String, nullable=True)
    cantidad_tratamientos_previos = Column(String, nullable=True)
    tipo_dosis = Column(String, nullable=True)
    cantidad_tratamientos_macro = Column(String, nullable=True)

    calificacion_tratamientos_previos = Column(Integer, nullable=True)
    riesgo_cannabis_se = Column(String, nullable=True)
    riesgo_psilocibina_se = Column(String, nullable=True)
    riesgo_cannabis_gb = Column(String, nullable=True)
    riesgo_psilocibina_gb = Column(String, nullable=True)
    comentario = Column(Text, nullable=True)

