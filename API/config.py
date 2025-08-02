from dotenv import load_dotenv
import os

load_dotenv()


MODELS_CONFIG = {
    "RANDOM_STATE_CANNABIS": 28,
    "RANDOM_STATE_PSILOCIBINA": 46,

    "TARGET_COL_CANNABIS_SE": 'Nivel de Riesgo Tratamiento Cannabis (SE)',
    "TARGET_COL_PSILOCIBINA_SE": 'Nivel de Riesgo Tratamiento Psilocibina (SE)',

    "TARGET_COL_CANNABIS_GB": 'Nivel de Riesgo Tratamiento Cannabis (GB)',
    "TARGET_COL_PSILOCIBINA_GB": 'Nivel de Riesgo Tratamiento Psilocibina (GB)',

    "BEST_MODEL_PSILOCIBINA": "../models/best_model_psilocibina.joblib",
    "BEST_MODEL_CANNABIS": "../models/best_model_cannabis.joblib",    
    "DATA_TEST": "../data/encuesta_test.csv"

}


DATABASE_CONFIG = {
    # "DATABASE_URL": os.getenv("DATABASE_URL"),
    # Pool size: cantidad de conexiones simultaneas a la base de datos
    "DATABASE_POOL_SIZE": int(os.getenv("DATABASE_POOL_SIZE", 3)),
    # Max overflow: cantidad de conexiones adicionales que se pueden crear si el pool está lleno (temporales)
    "DATABASE_MAX_OVERFLOW": int(os.getenv("DATABASE_MAX_OVERFLOW", 3)),
    "SUPABASE_URL": os.getenv("SUPABASE_URL"),
    "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY"),
    "SUPABASE_SERVICE_KEY": os.getenv("SUPABASE_SERVICE_KEY")
}
