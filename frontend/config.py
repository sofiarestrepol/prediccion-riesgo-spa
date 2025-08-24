from dotenv import load_dotenv
import os

load_dotenv()



DATABASE_CONFIG = {
    "PREDICT_EXTERNAL_RISK_URL": os.getenv("PREDICT_EXTERNAL_RISK_URL"),
    "DB_HOST": os.getenv("DB_HOST"),
    "DB_PORT": os.getenv("DB_PORT"),
    "DB_NAME": os.getenv("DB_NAME"),
    "DB_USER": os.getenv("DB_USER"),
    "DB_PASSWORD": os.getenv("DB_PASSWORD")
}

ADMIN_CONFIG = {
    "ADMIN_URL": os.getenv("ADMIN_URL")
}