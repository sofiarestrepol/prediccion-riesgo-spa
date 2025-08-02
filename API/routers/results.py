# Consultar los resultados de la prediccion
from fastapi import APIRouter
from services.interface_service import *
from utils.common import get_db
from supabase import create_client, Client
from config import DATABASE_CONFIG


router = APIRouter(tags=['results'])


@router.get("/results")
async def get_results(name: str):
    name = name.lower()

    supabase: Client = create_client(DATABASE_CONFIG['SUPABASE_URL'], DATABASE_CONFIG['SUPABASE_SERVICE_KEY'])
    response = supabase.table("users").select("*").ilike("nombre", name).execute()
    response = response.data[0]
    response.pop("autorizacion")
    response.pop("id")

    return response


