import pandas as pd
from config import DATABASE_CONFIG
import psycopg2


def get_database_connection():
    connection = psycopg2.connect(
        host=DATABASE_CONFIG['DB_HOST'],
        port=DATABASE_CONFIG['DB_PORT'],
        database=DATABASE_CONFIG['DB_NAME'],
        user=DATABASE_CONFIG['DB_USER'],
        password=DATABASE_CONFIG['DB_PASSWORD']
    )

    return connection

def load_data():
    conn = get_database_connection()
    query = "SELECT * FROM users;"
    df = pd.read_sql(query, conn)
    conn.close()
    return df