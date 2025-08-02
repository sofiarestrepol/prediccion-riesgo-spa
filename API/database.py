from sqlalchemy.ext.declarative import declarative_base  
# from sqlalchemy.orm import sessionmaker  
# from sqlalchemy import create_engine     
from config import DATABASE_CONFIG       

# Crea el motor de la base de datos utilizando la URL y parámetros de configuración proporcionados
# engine = create_engine(DATABASE_CONFIG["DATABASE_URL"],
# engine = create_engine(DATABASE_CONFIG["SUPABASE_URL"],
#                        pool_size=DATABASE_CONFIG["DATABASE_POOL_SIZE"],
#                        max_overflow=DATABASE_CONFIG["DATABASE_MAX_OVERFLOW"])

# # Crea una clase de sesión de SQLAlchemy que interactúa con la base de datos a través del motor configurado
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# DeclarativeBase es una clase base para definir modelos que representan tablas en la base de datos
Base = declarative_base()