from observer.observer_client import observer, Event, logger, nsroute
from data_server.redis_client import AsyncRedisClient as AsyncRC

import config
from cachetools import TTLCache

from redis import asyncio as aioredis

from typing import Dict

class RedisTable:
  MapListActive = "map_list_active"
  """Хранит активные карты"""

  MapListAll = "map_list_all"
  """Хранит все карты"""

  LastPlayers = "last_players"
  """Хранит всех игроков ранее заходившие"""

  BannedPlayers = "banned_players"
  """Хранит всех забаненных игроков"""

# -- init
rc: AsyncRC = AsyncRC(host=config.REDIS_HOST,
                              port=config.REDIS_PORT)

cache_players: TTLCache = TTLCache(maxsize=32, ttl=120)

# SECTION

def require_connection(func) -> callable:
  
  async def wrapper(*args, **kwargs) -> callable:
    if not rc.connected:
      return None
    
    if not (await rc.is_connected()):
      return None

    return await func(*args, **kwargs)
  
  return wrapper

# !SECTION

# -- run_rc
@observer.subscribe(Event.BE_READY)
async def run_rc():
  try:
    await rc.connect()
    logger.info(f"Redis: Сервер запущен на {rc.host}:{rc.port}, номер БД:{rc.db}")
  except Exception as err:
    logger.error(err)

# -- ev_add_ban
@observer.subscribe(Event.BC_CS_BAN)
@observer.subscribe(Event.BC_CS_BAN_OFFLINE)
@require_connection
async def ev_add_ban(data):
  """
    Добавляет игрока в список забанненых
  """
  await rc.list_add(RedisTable.BannedPlayers, data['target'])

# -- ev_unban_ban
@observer.subscribe(Event.BC_CS_UNBAN)
@require_connection
async def ev_unban_ban(data):
  """
    Убирает игрока из списка забанненых
  """
  await rc.list_delete(RedisTable.BannedPlayers, data['target'])

# -- ev_add_players_to_list
@observer.subscribe(Event.WBH_INFO)
@require_connection
async def ev_add_players_to_list(data):
  """
    Добавляет игроков в список LastPlayers
  """
  async with aioredis.Redis.from_pool(rc.pool)  as conn:
    async with conn.pipeline() as pipe:
      for player in data['current_players']:
        pipe.lrem(RedisTable.LastPlayers, 0, player["name"])
        pipe.rpush(RedisTable.LastPlayers, player["name"])

      await pipe.execute()
        

# -- ev_sync_maps
@observer.subscribe(Event.BC_CS_SYNC_MAPS)
@require_connection
async def ev_sync_maps(*args):
  """
    Удаляем все карты из редис
    Берем карты из SQL и добавляем их в редис
  """
  await rc.list_clear(RedisTable.MapListAll)
  await rc.list_clear(RedisTable.MapListActive)

  response = (await nsroute.call_route("/get_map_list"))

  if response is None:
    return
  
  async with aioredis.Redis.from_pool(rc.pool) as conn:
    async with conn.pipeline() as pipe:
      for map_name, activated in response:
        pipe.rpush(RedisTable.MapListAll, map_name)
        if activated:
          pipe.rpush(RedisTable.MapListActive, map_name)

      await pipe.execute()


# -- check_steam
@nsroute.create_route("/CheckSteam")
async def check_steam(steam_id: str):
  """
    Проверяем, есть ли связь в Редис, если да, то возвращаем
    Если нет, то делаем SQL запрос, и проверяем, существует ли
    Если в SQL существует -> сохраняем в редис и возвращаем ответ
    Если не существует -> Сохраняем в кэш как несуществующий(None) и возвращаем
  """

  # Проверяем
  if steam_id in cache_players:
    return cache_players[steam_id]
  
  # SQL
  response = (await nsroute.call_route("/check_user", steam_id))

  if response is None:
    cache_players[steam_id] = None

  else:
    cache_players[steam_id] = response

  return cache_players[steam_id]

# -- route_get_offline_players
@nsroute.create_route("/redis/get_offline_players")
@require_connection
async def route_get_offline_players() -> list:
  last_players: list = await rc.list_get(RedisTable.LastPlayers, 0)
  return [player.decode('utf-8') for player in last_players]

# -- route_get_banned_players
@nsroute.create_route("/redis/get_banned_players")
@require_connection
async def route_get_banned_players() -> list:
  banned_players: list = await rc.list_get(RedisTable.BannedPlayers, 0)
  return [player.decode('utf-8') for player in banned_players]

# -- route_get_map_list_active
@nsroute.create_route("/redis/get_map_list_active")
@require_connection
async def route_get_map_list_active() -> list:
  map_list: list = await rc.list_get(RedisTable.MapListActive, 0)
  return [map.decode('utf-8') for map in map_list]

# -- route_get_map_list_all
@nsroute.create_route("/redis/get_map_list_all")
@require_connection
async def route_get_map_list_all() -> list:
  map_list: list = await rc.list_get(RedisTable.MapListAll, 0 )
  return [map.decode('utf-8') for map in map_list]

# -- route_update_map_list
@nsroute.create_route("/redis/update_map_list")
@require_connection
async def route_update_map_list(type, map_name, activated=None):
  if type == "add":
    await rc.list_add(RedisTable.MapListAll, map_name)
    if activated == 1:
      await rc.list_add(RedisTable.MapListActive, map_name)

    
  elif type == "delete":
    await rc.list_delete(RedisTable.MapListAll, map_name)
    await rc.list_delete(RedisTable.MapListActive, map_name)

    
  elif type == "update":
    if activated is None:
      return

    if activated == 1:
      # Нужно удалить, чтобы не было повторений
      await rc.list_delete(RedisTable.MapListActive, map_name)
      await rc.list_add(RedisTable.MapListActive, map_name)
    elif activated == 0:
      await rc.list_delete(RedisTable.MapListActive, map_name)