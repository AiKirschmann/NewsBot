#!/usr/bin/env python3

from database.connection import db_manager
from utils.logger import setup_logger

logger = setup_logger(__name__)

def check_database():
    """Проверка структуры базы данных"""
    try:
        with db_manager.get_db_session() as conn:
            with conn.cursor() as cur:
                # Проверяем таблицы
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                tables = cur.fetchall()
                print("\nСуществующие таблицы:")
                for table in tables:
                    print(f"- {table[0]}")
                    
                # Проверяем структуру каждой таблицы
                for table in tables:
                    cur.execute(f"""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = '{table[0]}'
                    """)
                    columns = cur.fetchall()
                    print(f"\nСтруктура таблицы {table[0]}:")
                    for col in columns:
                        print(f"  - {col[0]}: {col[1]}")
                
        logger.info("Database check completed successfully")
    except Exception as e:
        logger.error(f"Error checking database: {e}")
        raise

if __name__ == "__main__":
    print("Проверяем структуру базы данных...")
    check_database()
