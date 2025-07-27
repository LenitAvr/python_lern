import psycopg2
from psycopg2 import sql
import sys

# Параметры подключения
DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "postgres"
DB_PASSWORD = "1234"
DB_NAME = "gamedb"

def create_database():
    conn = None
    try:
        # Подключение к системной базе
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname="postgres",
            options="-c client_encoding=utf8"
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Проверка существования базы данных
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        if cursor.fetchone():
            print(f"База данных '{DB_NAME}' уже существует")
        else:
            # Создание базы с UTF-8 кодировкой
            cursor.execute(
                sql.SQL("CREATE DATABASE {} ENCODING 'UTF8' LC_COLLATE 'C' LC_CTYPE 'C' TEMPLATE template0")
                .format(sql.Identifier(DB_NAME)))
            print(f"База данных '{DB_NAME}' создана с кодировкой UTF-8")

    except psycopg2.Error as e:
        print(f"Ошибка при создании базы данных: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

def create_tables():
    conn = None
    try:
        # Подключение к новой базе
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME,
            options="-c client_encoding=utf8"
        )
        cursor = conn.cursor()

        # Исправленные запросы с закрывающими скобками
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS providers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(255)
            )
        """)  # Закрывающая скобка добавлена

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                price NUMERIC(10, 2) NOT NULL,
                is_published BOOLEAN DEFAULT TRUE,
                provider_id INTEGER REFERENCES providers(id)
            )
        """)  # Закрывающая скобка добавлена

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_games_provider_id ON games(provider_id)
        """)

        conn.commit()
        print("Таблицы созданы успешно!")

    except psycopg2.Error as e:
        print(f"Ошибка при создании таблиц: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_database()
    create_tables()