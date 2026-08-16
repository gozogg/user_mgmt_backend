import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

def get_connection():
    return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )

def fetch_all(query, params=None):
    """SELECT"""
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(query, params or ())
        rows = cur.fetchall()
        cur.close()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def execute(query, params=None):
    """INSERT/DELETE/UPDATE"""
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(query, params=None)
        cur.commit()
        cur.close()
    finally:
        conn.close()



def main():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        print("Connected successfully!")

        cur = conn.cursor()
        cur.execute("SELECT version();")
        print("Postgres version: ", cur.fetchone())

        cur.close()
        conn.close()

    except Exception as e:
        print("Connection failed: ", e)

if __name__ == "__main__":
    main()