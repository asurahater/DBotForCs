import os
import sys
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import components.asyncsql as asyncsql
# from components.asyncsql import AioMysql, QueryError

async def main():
    # Создаем экземпляр AioMysql
    db = asyncsql.AioMysql(host='127.0.0.1', port=3306, user='root', password='', db='mysql_test')
    
    # Подключаемся к базе данных
    await db.connect()
    
    # Пример вставки данных
    try:
        query = "SELECT * FROM users"

        counter = 1
        async for row in db.fetch_iter(query, batch_size=10):
            print(f"{counter}. {row}")
            counter+=1

    except asyncsql.QueryError as e:
        print(f"Ошибка при вставке данных: {e}")

    await db.close()

if __name__ == '__main__':
    asyncio.run(main())
