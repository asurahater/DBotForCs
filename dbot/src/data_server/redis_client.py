from redis import asyncio as aioredis
from typing import Optional, Union, List

# SECTION RedisError
class RedisError(Exception):
  """Базовый класс для исключений Redis."""
  pass
# -- RedisConnectionError
class RedisConnectionError(RedisError):
  """Исключение, возникающее при ошибке подключения к Redis."""
  pass

# -- RedisSetError
class RedisSetError(RedisError):
  """Исключение, возникающее при ошибке установки значения в Redis."""
  pass

# -- RedisGetError
class RedisGetError(RedisError):
  """Исключение, возникающее при ошибке получения значения из Redis."""
  pass

# -- RedisDeleteError
class RedisDeleteError(RedisError):
  """Исключение, возникающее при ошибке удаления ключа из Redis."""
  pass

# -- RedisExistsError
class RedisExistsError(RedisError):
  """Исключение, возникающее при ошибке проверки существования ключа в Redis."""
  pass

# -- RedisKeysError
class RedisKeysError(RedisError):
  """Исключение, возникающее при ошибке получения ключей из Redis."""
  pass
# !SECTION

# SECTION Class AsyncRedisClient
class AsyncRedisClient:
  # -- __init__()
  def __init__(self, host: str = '127.0.0.1', port: int = 6379, db: int = 0) -> None:
    """Инициализация клиента Redis."""
    self.host: str = host
    self.port: int = port
    self.db: int = db
    self.pool = None

  # -- connect()
  async def connect(self) -> None:
    """Подключение к Redis с использованием пула соединений."""
    try:
      self.pool = aioredis.ConnectionPool.from_url(f"redis://{self.host}:{self.port}/{self.db}")

      async with aioredis.Redis.from_pool(self.pool) as conn:
        await conn.ping()
    except aioredis.RedisError as e:
      raise RedisConnectionError(f"Ошибка подключения к Redis: {e}")

  # -- set_hash()
  async def set_hash(self, table: str, key: str, value: Union[str, bytes]) -> None:
    """Устанавливает значение в хэш (таблицу) по ключу."""
    if not self.pool:
      raise RedisConnectionError("Клиент Redis не инициализирован.")

    try:
      async with aioredis.Redis.from_pool(self.pool) as conn:
        await conn.hset(table, key, value)
    except aioredis.RedisError as e:
      raise RedisSetError(f"Ошибка при установке значения в таблицу '{table}': {e}")

  # -- get_hash()
  async def get_hash(self, table: str, key: str) -> Optional[Union[str, bytes]]:
    """Получает значение из хэша (таблицы) по ключу."""
    if not self.pool:
      raise RedisConnectionError("Клиент Redis не инициализирован.")

    try:
      async with aioredis.Redis.from_pool(self.pool) as conn:
        value = await conn.hget(table, key)
        return None if value is None else value.decode('utf-8')  # Декодируем значение, если оно не None
    except aioredis.RedisError as e:
      raise RedisGetError(f"Ошибка при получении значения из таблицы '{table}': {e}")

  # -- delete_hash()
  async def delete_hash(self, table: str, key: str) -> int:
    """Удаляет ключ из хэша (таблицы)."""
    if not self.pool:
      raise RedisConnectionError("Клиент Redis не инициализирован.")

    try:
      async with aioredis.Redis.from_pool(self.pool) as conn:
        return await conn.hdel(table, key)
    except aioredis.RedisError as e:
      raise RedisDeleteError(f"Ошибка при удалении ключа из таблицы '{table}': {e}")

  # -- exists_hash()
  async def exists_hash(self, table: str, key: str) -> bool:
    """Проверяет, существует ли ключ в хэше (таблице)."""
    if not self.pool:
      raise RedisConnectionError("Клиент Redis не инициализирован.")

    try:
      async with aioredis.Redis.from_pool(self.pool) as conn:
        return await conn.hexists(table, key)
    except aioredis.RedisError as err:
      raise RedisExistsError(f"Ошибка при проверке существования ключа в таблице '{table}': {err}")

  # -- keys_hash()
  async def keys_hash(self, table: str) -> List[str]:
    """Возвращает список всех ключей в хэше (таблице)."""
    if not self.pool:
      raise RedisConnectionError("Клиент Redis не инициализирован.")

    try:
      async with aioredis.Redis.from_pool(self.pool) as conn:
        return await conn.hkeys(table)
    except aioredis.RedisError as e:
      raise RedisKeysError(f"Ошибка при получении ключей из таблицы '{table}': {e}")

  # -- list_add()
  async def list_add(self, table: str, value: str) -> None:
    """Добавляет значение в конец списка, связанного с таблицей."""
    async with aioredis.Redis.from_pool(self.pool) as conn:
      await conn.rpush(table, value)

  # -- list_get()
  async def list_get(self, table: str, from_: int, to_: int=-1) -> List[str]:
    """Возвращает последние n значений из списка, связанного с таблицей."""
    async with aioredis.Redis.from_pool(self.pool) as conn:
      return await conn.lrange(table, from_, to_)  # Получаем последние n значений
    
  # -- list_delete()
  async def list_delete(self, table: str, value: str, count: int = 0) -> None:
    """Удаляет элемент из списка, связанного с таблицей.
    
    :param table: Имя таблицы (ключ).
    :param value: Значение, которое нужно удалить.
    :param count: Количество вхождений для удаления.
                  Если count > 0, удаляет только первые count вхождений.
                  Если count < 0, удаляет только последние count вхождений.
                  Если count = 0, удаляет все вхождения.
    """
    async with aioredis.Redis.from_pool(self.pool) as conn:
      await conn.lrem(table, count, value)

  #  -- list_clear()
  async def list_clear(self, table: str) -> None:
    """Очищает содержимое списка, оставляя сам ключ."""
    if not self.pool:
      raise RedisConnectionError("Клиент Redis не инициализирован.")

    try:
      async with aioredis.Redis.from_pool(self.pool) as conn:
        await conn.ltrim(table, 1, 0) 
    except aioredis.RedisError as e:
      raise RedisError(f"Ошибка при очистке списка '{table}': {e}")


  # -- list_exists()
  async def list_exists(self, table: str, value: str) -> bool:
    """Проверяет, существует ли значение в списке, связанном с таблицей."""
    async with aioredis.Redis.from_pool(self.pool) as conn:
      list_values = await conn.lrange(table, 0, -1)
      return value.encode('utf-8') in list_values


  # -- close()
  async def close(self) -> None:
    """Закрывает соединение с Redis."""
    if self.pool:
      await self.pool.disconnect()
      
# !SECTION
