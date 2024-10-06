from observer.observer_client import observer, logger, nsroute, Event, Param
from data_server.asyncsql import AioMysql, QueryError, ConnectionError as aioConnectionError

import discord
import re

import config

mysql: AioMysql = AioMysql(host=config.DB_HOST,
                           port=config.DB_PORT,
                           user=config.DB_USER,
                           password=config.DB_PASSWORD,
                           db=config.DB_NAME)

# SECTION Utility

# -- @require_connection
def require_connection(func) -> callable:
  
  async def wrapper(*args, **kwargs) -> callable:
    if mysql.is_connected():
      return await func(*args, **kwargs)
    
    if 'data' in kwargs and kwargs['data']:
      await kwargs['data'][Param.Interaction].followup.send('Нет соединения с базой данных', ephemeral=True)
        
    logger.error("MySQL: Нет связи с БД")
  
  return wrapper

# -- steam_record_exist
@require_connection
async def steam_record_exist(user_id: str, steam_id: str):
  query = "SELECT COUNT(*) FROM users WHERE discord_id = %s OR steam_id = %s"
  query_values = (user_id, steam_id)

  try:
    response = await mysql.execute_select(query, query_values)

    if not response or not response[0]:
      return False  # Если нет результатов, возвращаем False

    rows = response[0][0]

    return rows != 0
  except QueryError as err:
    logger.error(f"{err}")

# -- map_record_exist
@require_connection
async def map_record_exist(map_name: str):
  query = "SELECT COUNT(*) FROM maps WHERE map_name = %s"
  query_values = (map_name,)

  try:
    response = await mysql.execute_select(query, query_values)

    if not response or not response[0]:
      return False  # Если нет результатов, возвращаем False

    rows = response[0][0]

    return rows != 0
  except QueryError as err:
    logger.error(f"{err}")
    return None

# -- check_steam_id
def check_steam_id(steam_id: str):
  pattern = r'^(STEAM|VALVE)_[0-9]:[0-9]:[0-9]{1,12}$'
  return bool(re.match(pattern, steam_id))

# !SECTION

# -- ev_ready
@observer.subscribe(Event.BE_READY)
async def ev_ready():
  try:
    await mysql.connect()
    logger.info("MySQL: Успешно подключен")
  except aioConnectionError as err:
    logger.error(f"MySQL: {err}")

# -- ev_reg
@observer.subscribe(Event.BC_REG)
@require_connection
async def ev_reg(data):
  interaction: discord.Interaction = data[Param.Interaction]
  user_id: str = str(interaction.user.id)
  steam_id: str = data['steam_id']

  # проверяем стим айди на валидность
  if not check_steam_id(steam_id):
    await interaction.followup.send('Неправильный формат SteamID', ephemeral=True)
    return

  # проверяем существует ли запись
  if await steam_record_exist(user_id, steam_id):
    await interaction.followup.send(f'Данные для данного SteamID или вашего аккаунта уже существуют.', ephemeral=True)
    return

  # сохраняем
  username = interaction.user.name
  ds_username = interaction.user.display_name

  query = "INSERT INTO users (discord_id, ds_name, ds_display_name, steam_id) VALUES (%s, %s, %s, %s)"
  query_values = (user_id, username, ds_username, steam_id)

  try:
    rows = await mysql.execute_change(query, query_values)
    if rows == 0:
      await interaction.followup.send('Не удалось сохранить данные', ephemeral=True)
    else:
      await interaction.followup.send('Данные сохранены!', ephemeral=True)
  except QueryError as err:
    logger.error(f"{err}")
    await interaction.followup.send('Ошибка!', ephemeral=True)

# -- ev_unreg
@observer.subscribe(Event.BC_UNREG)
@require_connection
async def ev_unreg(data):
  interaction: discord.Interaction = data[Param.Interaction]
  user_id = str(interaction.user.id)

  query = "DELETE FROM users WHERE discord_id = %s"
  query_values = (user_id)

  try:
    rows = await mysql.execute_change(query, query_values)

    if rows == 0:
      await interaction.followup.send('Данные не найдены', ephemeral=True)
    else:
      await interaction.followup.send('Данные удалены!', ephemeral=True)

  except QueryError as err:
    logger.error(f"{err}")
    await interaction.followup.send('Ошибка!', ephemeral=True)
    
# -- ev_map_add
@observer.subscribe(Event.BC_DB_MAP_ADD)
@require_connection
async def ev_map_add(data):
  interaction: discord.Interaction = data[Param.Interaction]

  # Проверяем в БД на сущестовование
  response = await map_record_exist(data['map_name'])
  if response:
    await interaction.followup.send(f'Такая карта уже существует', ephemeral=True)
    return
  if response is None:
    await interaction.followup.send(f'Произошла ошибка!', ephemeral=True)
    return
  

  # Сохраняем в БД
  query = "INSERT INTO maps (map_name, activated, min_players, max_players, priority) VALUES (%s, %s, %s, %s, %s)"
  query_values = (data['map_name'], data['activated'], data['min_players'], data['max_players'], data['priority'])

  try:
    rows = await mysql.execute_change(query, query_values)
    if rows == 0:
      await interaction.followup.send('Не удалось добавить карту', ephemeral=True)
    else:
      await interaction.followup.send('Карта добавлена!', ephemeral=True)
  except QueryError as err:
    logger.error(f"{err}")
    await interaction.followup.send('Ошибка!', ephemeral=True)

  # Сохраняем в редис
  await nsroute.call_route("/redis/update_map_list", "add", data['map_name'], data['activated'])

 # -- ev_map_delete
@observer.subscribe(Event.BC_DB_MAP_DELETE)
@require_connection
async def ev_map_delete(data):
  interaction: discord.Interaction = data[Param.Interaction]

  # Удаляем из БД
  query = "DELETE FROM maps WHERE map_name = %s"
  query_values = (data['map_name'])

  try:
    rows = await mysql.execute_change(query, query_values)
    if rows == 0:
      await interaction.followup.send('Такой карты не существует', ephemeral=True)
    else:
      await interaction.followup.send('Карта удалена!', ephemeral=True)
  except QueryError as err:
    logger.error(f"{err}")
    await interaction.followup.send('Ошибка!', ephemeral=True)

  # Удаляем из редис
  await nsroute.call_route("/redis/update_map_list", "delete", data['map_name'])
    
 # -- ev_map_update
@observer.subscribe(Event.BC_DB_MAP_UPDATE)
@require_connection
async def ev_map_update(data):
  interaction: discord.Interaction = data[Param.Interaction]

  # Проверяем в БД на сущестовование
  response = await map_record_exist(data['map_name'])
  if not response:
    await interaction.followup.send(f'Карты не существует', ephemeral=True)
    return
  if response is None:
    await interaction.followup.send(f'Произошла ошибка!', ephemeral=True)
    return
  
  updates: list = []
  query_values: list = []

  if data['activated'] is not None:
    updates.append("activated = %s")
    query_values.append(data['activated'])
      
  if data['min_players'] is not None:
    updates.append("min_players = %s")
    query_values.append(data['min_players'])
      
  if data['max_players'] is not None:
    updates.append("max_players = %s")
    query_values.append(data['max_players'])
      
  if data['priority'] is not None:
    updates.append("priority = %s")
    query_values.append(data['priority'])

  if not updates:
    await interaction.followup.send('Вы не выбрали что обновить!', ephemeral=True)
    return

  # Обновляем в БД
  query = f"UPDATE maps SET {', '.join(updates)} WHERE map_name = %s"
  query_values.append(data['map_name'])

  try:
    rows = await mysql.execute_change(query, query_values)
    if rows == 0:
      await interaction.followup.send('Такой карты не существует', ephemeral=True)
    else:
      await interaction.followup.send('Карта Обновлена!', ephemeral=True)
  except QueryError as err:
    logger.error(f"{err}")
    await interaction.followup.send('Ошибка!', ephemeral=True)

  # Обновляем в редис
  await nsroute.call_route("/redis/update_map_list", "update", data['map_name'], data['activated'])
  
# -- ev_member_update
@observer.subscribe(Event.BE_MEMBER_UPDATE)
@require_connection
async def ev_member_update(data):
  ds_id = data['user_id']
  new_username = data['new_username']

  query = "UPDATE users SET ds_display_name = %s WHERE discord_id = %s"
  query_values = (new_username, str(ds_id))

  try:
    await mysql.execute_change(query, query_values)
  except QueryError as err:
    logger.error(f"{err}")

# -- (route) check_user
@nsroute.create_route("/check_user")
@require_connection
async def route_check_user(steam_id):
  query = "SELECT discord_id FROM users WHERE steam_id = %s"
  query_values = (steam_id, )

  try:
    response = await mysql.execute_select(query, query_values)

    if not response or not response[0]:
      return None  # Если нет результатов, возвращаем False

    id = response[0][0]

    return id
  except QueryError as err:
    logger.error(f"{err}")

# - (route) get_map_list
@nsroute.create_route("/get_map_list")
@require_connection
async def route_get_map_list():
  query = "SELECT map_name, activated FROM maps"

  try:
    response = await mysql.execute_select(query)

    if not response or not response[0]:
      return None  # Если нет результатов, возвращаем False

    return response
  except QueryError as err:
    logger.error(f"{err}")