import aiomysql
from typing import AsyncIterator, List, Tuple, Any, Optional

# SECTION AioMysqlError
class AioMysqlError(Exception):
  """Базовый класс для исключений AioMysql."""
  pass

# -- ConnectionError
class ConnectionError(AioMysqlError):
  """Исключение для ошибок подключения к базе данных."""
  pass

# -- QueryError
class QueryError(AioMysqlError):
  """Исключение для ошибок выполнения SQL-запросов."""
  pass

# -- MultipleQueryError
class MultipleQueryError(AioMysqlError):
  """Исключение для ошибок выполнения нескольких SQL-запросов."""
  pass

# -- TransactionError
class TransactionError(AioMysqlError):
  """Исключение для ошибок, связанных с транзакциями."""
  pass

# !SECTION

# SECTION AioMysql
class AioMysql:
  # -- __init__()
  def __init__(self, host: str, port: int, user: str, password: str, db: str) -> None:
    self.host: str = host
    self.port: int = port
    self.user: str = user
    self.password: str = password
    self.db: str = db
    self.pool: Optional[aiomysql.Pool] = None
    self.conn: Optional[aiomysql.Connection] = None

  # -- connect()
  async def connect(self) -> None:
    """Создает пул соединений с базой данных."""
    try:
      self.pool = await aiomysql.create_pool(
        host=self.host,
        port=self.port,
        user=self.user,
        password=self.password,
        db=self.db
      )
    except aiomysql.Error as e:
      raise ConnectionError(f"Ошибка при подключении к базе данных: {e}")
    
  def is_connected(self) -> bool:
    """Проверяет, открыт ли пул соединений."""
    return self.pool is not None and not self.pool.closed

  # -- execute_one()
  async def execute_one(self, query: str, args: Optional[Tuple[Any, ...]] = ()) -> Tuple[int, Optional[List[Tuple[Any, ...]]]]:
    """Выполняет SQL-запрос и возвращает количество затронутых строк и результат."""
    try:
      async with self.pool.acquire() as conn:
        async with conn.cursor() as cursor:
          await cursor.execute(query, args)
          affected_rows = cursor.rowcount  # Получаем количество затронутых строк
          
          if cursor.description:  # Проверяем, есть ли результат
            result = await cursor.fetchall()
            return affected_rows, result
          
          await conn.commit()
          return affected_rows, None  # Если нет результата
    except aiomysql.Error as e:
      raise QueryError(f"Ошибка при выполнении запроса: {e}. Запрос: {query}, Параметры: {args}")
    except Exception as e:
      raise QueryError(f"Неожиданная ошибка: {e}. Запрос: {query}, Параметры: {args}")

  # -- execute_change()
  async def execute_change(self, query: str, args: Optional[Tuple[Any, ...]] = ()) -> int:
    """Выполняет SQL-запрос, изменяющий данные, и возвращает количество затронутых строк."""
    try:
      async with self.pool.acquire() as conn:
        async with conn.cursor() as cursor:
          await cursor.execute(query, args)
          affected_rows = cursor.rowcount
          await conn.commit()  # Коммитим изменения
          return affected_rows
    except aiomysql.Error as e:
      raise QueryError(f"Ошибка при выполнении запроса: {e}. Запрос: {query}, Параметры: {args}")
    except Exception as e:
      raise QueryError(f"Неожиданная ошибка: {e}. Запрос: {query}, Параметры: {args}")

  # -- execute_select()
  async def execute_select(self, query: str, args: Optional[Tuple[Any, ...]] = ()) -> List[Tuple[Any, ...]]:
    """Выполняет SQL-запрос на выборку данных и возвращает результат."""
    try:
      async with self.pool.acquire() as conn:
        async with conn.cursor() as cursor:
          await cursor.execute(query, args)
          result = await cursor.fetchall()  # Получаем результат
          return result
    except aiomysql.Error as e:
      raise QueryError(f"Ошибка при выполнении запроса: {e}. Запрос: {query}, Параметры: {args}")
    except Exception as e:
      raise QueryError(f"Неожиданная ошибка: {e}. Запрос: {query}, Параметры: {args}")


  # -- exec_many()
  async def exec_many(self, query: str, args_list: List[Tuple[Any, ...]]) -> None:
    """Выполняет один и тот же SQL-запрос несколько раз с разными наборами параметров."""
    try:
      async with self.pool.acquire() as conn:
        async with conn.cursor() as cursor:
          await cursor.executemany(query, args_list)
          await conn.commit()
    except aiomysql.Error as e:
      raise MultipleQueryError(f"Ошибка при выполнении нескольких запросов: {e}. Запрос: {query}, Параметры: {args_list}")
    except Exception as e:
      raise MultipleQueryError(f"Неожиданная ошибка: {e}. Запрос: {query}, Параметры: {args_list}")

  # -- fetch_iter()
  async def fetch_iter(self, query: str, *, args: Optional[Tuple[Any, ...]] = (), batch_size: int = 100) -> AsyncIterator[Tuple[Any, ...]]:
    """Асинхронный итератор для выборки данных по частям."""
    try:
      async with self.pool.acquire() as conn:
        async with conn.cursor() as cursor:
          await cursor.execute(query, args)
          while True:
            rows = await cursor.fetchmany(size=batch_size)  # Получаем указанное количество строк за раз
            if not rows:
              break
            for row in rows:
              yield row  # Возвращаем строку
    except aiomysql.Error as e:
      raise QueryError(f"Ошибка при выборке данных: {e}. Запрос: {query}, Параметры: {args}")
    except Exception as e:
      raise QueryError(f"Неожиданная ошибка: {e}. Запрос: {query}, Параметры: {args}")

  # -- close()
  async def close(self) -> None:
    """Закрывает пул соединений."""
    if not self.pool:
        raise ConnectionError("Пул соединений уже закрыт.")
    self.pool.close()
    await self.pool.wait_closed()
    self.pool = None
      
# !SECTION

# SECTION Transaction
class Transaction:
  # -- __init__()
  def __init__(self, pool: aiomysql.Pool) -> None:
    """Инициализирует объект транзакции с пулом соединений."""
    self.pool: aiomysql.Pool = pool
    self.conn: Optional[aiomysql.Connection] = None  # Соединение, используемое в транзакции
  
  # -- begin()
  async def begin(self) -> None:
    """Начинает транзакцию."""
    if not self.pool:
      raise ConnectionError("Пул соединений не инициализирован.")
    try:
      self.conn = await self.pool.acquire()  # Получаем соединение
      await self.conn.begin()  # Начинаем транзакцию
    except aiomysql.Error as e:
      raise TransactionError(f"Ошибка при начале транзакции: {e}")
  
  # -- execute()
  async def execute(self, query: str, args: Optional[Tuple[Any, ...]] = ()) -> Tuple[int, Optional[List[Tuple[Any, ...]]]]:
    """Выполняет SQL-запрос в рамках текущей транзакции.
    
    Args:
      query (str): SQL-запрос для выполнения.
      args (Optional[Tuple[Any, ...]]): Параметры для SQL-запроса.

    Returns:
      Tuple[int, Optional[List[Tuple[Any, ...]]]]: Количество затронутых строк и результат запроса.
    """
    if not self.conn:
      raise TransactionError("Нет активной транзакции.")
    try:
      async with self.conn.cursor() as cursor:
        await cursor.execute(query, args)  # Выполняем запрос
        affected_rows = cursor.rowcount  # Получаем количество затронутых строк
        result = await cursor.fetchall()  # Возвращаем результаты
        return affected_rows, result
    except aiomysql.Error as e:
      raise TransactionError(f"Ошибка при выполнении запроса: {e}. Запрос: {query}, Параметры: {args}")
  
  # -- commit()
  async def commit(self) -> None:
    """Коммитит текущую транзакцию."""
    if not self.conn:
      raise TransactionError("Нет активной транзакции.")
    try:
      await self.conn.commit()  # Коммитим изменения
    except aiomysql.Error as e:
      raise TransactionError(f"Ошибка при коммите транзакции: {e}")
  
  # -- rollback()
  async def rollback(self) -> None:
    """Откатывает текущую транзакцию."""
    if not self.conn:
      raise TransactionError("Нет активной транзакции.")
    try:
      await self.conn.rollback()  # Откатываем изменения
    except aiomysql.Error as e:
      raise TransactionError(f"Ошибка при откате транзакции: {e}")
  
  # -- close()
  async def close(self) -> None:
    """Закрывает соединение."""
    if self.conn:
      await self.pool.release(self.conn)  # Освобождаем соединение
      self.conn = None  # Сбрасываем соединение

# !SECTION