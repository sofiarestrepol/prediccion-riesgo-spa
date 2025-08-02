from dotenv import load_dotenv
import os

load_dotenv()



DATABASE_CONFIG = {
    "PREDICT_EXTERNAL_RISK_URL": os.getenv("PREDICT_EXTERNAL_RISK_URL")
}