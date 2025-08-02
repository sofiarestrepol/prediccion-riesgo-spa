from routers import surveys, interface, results
from fastapi import FastAPI
# from database import engine
import models


# Crear aplicación FastAPI
app = FastAPI()


app.include_router(surveys.router)
app.include_router(interface.router)
app.include_router(results.router)

# models.Base.metadata.create_all(bind=engine)

