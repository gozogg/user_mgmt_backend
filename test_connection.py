import psycopg2

DB_HOST = "database-1.cn6ic048q6et.us-east-2.rds.amazonaws.com"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "2f9mVvV2dvBk7vWgg5c7" #updated password

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