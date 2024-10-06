from observer.observer_client import logger, observer, Event, Param, Color, nsroute
from cs_server.csrcon import CSRCON, ConnectionError as CSConnectionError, CommandExecutionError

import discord

import config

# -- init
cs_server: CSRCON = CSRCON(host=config.CS_HOST,
                           password=config.CS_RCON_PASSWORD)

# SECTION Utlities

# -- @require_connection
def require_connection(func) -> callable:
  
  async def wrapper(*args, **kwargs) -> callable:
    if cs_server.connected:
      return await func(*args, **kwargs)

    if 'data' in kwargs and kwargs['data']:
      await kwargs['data'][Param.Interaction].followup.send('Нет подключения к серверу', ephemeral=True)
    
    logger.error("CS Server: Нет связи с CS")
  
  return wrapper

# !SECTION

# SECTION Events
# -- get_status 
@observer.subscribe(Event.BT_CS_Status)
async def get_status():
  if not cs_server.connected:
    return
  
  try:
    await cs_server.exec("ultrahc_ds_get_info")
  except CommandExecutionError as err:
    logger.error(f"CS Server: {err}")
    await cs_server.disconnect()
    await observer.notify(Event.CS_DISCONNECTED)

# -- on_ready connect
@observer.subscribe(Event.BE_READY)
@nsroute.create_route("/connect_to_cs")
async def connect():
  try:
    await cs_server.connect_to_server()
    logger.info(f"CS Server: Успешно подключен")
    
    await observer.notify(Event.CS_CONNECTED)

  except CSConnectionError as err:
    logger.error(f"CS Server: {err}")

@observer.subscribe(Event.BE_MESSAGE)
@require_connection
async def send_message(data):
  message: discord.Message = data[Param.Message]

  send_msg = "\"" + message.author.display_name + "\"" + " " + "\"" + message.content + "\""
  command = f"ultrahc_ds_send_msg {send_msg}"

  try:
    await cs_server.exec(command)
  except CommandExecutionError as err:
    logger.error(f"CS Server: {err}")



# !SECTION
# SECTION BotCommand Events

# -- connect_to_cs
@observer.subscribe(Event.BC_CONNECT_TO_CS)
async def cmd_connect_to_cs(data):
  await cs_server.disconnect()
  interaction: discord.Interaction = data[Param.Interaction]

  try:
    await cs_server.connect_to_server()
    logger.info(f"CS Server: Успешно подключен")
    await interaction.followup.send(content="Успешно подключено!", ephemeral=True)
  except CSConnectionError as err:
    logger.error(f"CS Server: {err}")
    await interaction.followup.send(content="Невозможно подключиться!", ephemeral=True)

# -- rcon
@observer.subscribe(Event.BC_CS_RCON)
@require_connection
async def cmd_rcon(data):
  interaction: discord.Interaction = data[Param.Interaction]
  command: str = data["command"]
  
  try:
    await cs_server.exec(command)
    logger.info(f"CS Server: выполнена команда: {command}")
    await interaction.followup.send(content="Команда выполнена!", ephemeral=True)
  except CommandExecutionError as err:
    logger.error(f"CS Server: {err}")
    await interaction.followup.send(content="Не удалось выполнить команду!", ephemeral=True)

# -- kick
@observer.subscribe(Event.BC_CS_KICK)
@require_connection
async def cmd_kick(data):
  interaction: discord.Interaction = data[Param.Interaction]
  caller_name: str = interaction.user.display_name
  target: str = data['target']
  reason: str = data['reason']

  command = f"ultrahc_ds_kick_player \"{target}\" \"{reason}\""
  
  try:
    await cs_server.exec(command)
    logger.info(f"CS Server: {caller_name} кикнул игрока {target} по причине {reason}")

    snd = f"```ansi\n{Color.Blue}{caller_name}{Color.Default} кикнул игрока: {Color.Blue}{target}{Color.Default} по причине: {reason}```"
    await interaction.channel.send(content=snd)
    await interaction.delete_original_response()
  except CommandExecutionError as err:
    logger.error(f"CS Server: {err}")
    await interaction.followup.send(content="Не удалось кикнуть игрока", ephemeral=True)

# -- ban
@observer.subscribe(Event.BC_CS_BAN)
@require_connection
async def cmd_ban(data):
  interaction: discord.Interaction = data[Param.Interaction]
  caller_name: str = interaction.user.display_name
  target: str = data['target']
  minutes: int = data['minutes']
  reason: str = data['reason']

  command = f"amx_ban \"{target}\" \"{minutes}\" \"{reason}\""
  
  try:
    await cs_server.exec(command)
    logger.info(f"CS Server: {caller_name} забанил игрока {target} на {minutes} минут по причине {reason}")

    snd = f"```ansi\n{Color.Blue}{caller_name}{Color.Default} забанил игрока: {Color.Blue}{target}{Color.Default} на {minutes} минут по причине: {reason}```"
    await interaction.channel.send(content=snd)
    await interaction.delete_original_response()
  except CommandExecutionError as err:
    logger.error(f"CS Server: {err}")
    await interaction.followup.send(content="Не удалось забанить игрока", ephemeral=True)

# -- ban_offline
@observer.subscribe(Event.BC_CS_BAN_OFFLINE)
@require_connection
async def cmd_ban_offline(data):
  interaction: discord.Interaction = data[Param.Interaction]
  caller_name: str = interaction.user.display_name
  target: str = data['target']
  minutes: int = data['minutes']
  reason: str = data['reason']

  command = f"amx_addban \"{target}\" \"{minutes}\" \"{reason}\""
  
  try:
    await cs_server.exec(command)
    logger.info(f"CS Server: {caller_name} забанил игрока {target} на {minutes} минут по причине {reason}")

    snd = f"```ansi\n{Color.Blue}{caller_name}{Color.Default} забанил игрока: {Color.Blue}{target}{Color.Default} на {minutes} минут по причине: {reason}```"
    await interaction.channel.send(content=snd)
    await interaction.delete_original_response()
  except CommandExecutionError as err:
    logger.error(f"CS Server: {err}")
    await interaction.followup.send(content="Не удалось забанить игрока", ephemeral=True)

# -- unban
@observer.subscribe(Event.BC_CS_UNBAN)
@require_connection
async def cmd_unban(data):
  interaction: discord.Interaction = data[Param.Interaction]
  caller_name: str = interaction.user.display_name
  target: str = data['target']

  command = f"amx_unban \"{target}\""
  
  try:
    await cs_server.exec(command)
    logger.info(f"CS Server: {caller_name} разбанил игрока {target}")

    snd = f"```ansi\n{Color.Blue}{caller_name}{Color.Default} разбанил игрока: {Color.Blue}{target}{Color.Default}```"
    await interaction.channel.send(content=snd)
    await interaction.delete_original_response()
  except CommandExecutionError as err:
    logger.error(f"CS Server: {err}")
    await interaction.followup.send(content="Не удалось разбанить игрока", ephemeral=True)

# -- sync_maps
@observer.subscribe(Event.BC_CS_SYNC_MAPS)
@require_connection
async def cmd_sync_maps(data):
  interaction: discord.Interaction = data[Param.Interaction]
  caller_name: str = interaction.user.display_name

  command = "ultrahc_ds_reload_map_list"
  
  try:
    await cs_server.exec(command)

    logger.info(f"CS Server: {caller_name} синхронизировал карты")
    await interaction.followup.send(content="Успешно", ephemeral=True)
  except CommandExecutionError as err:
    logger.error(f"CS Server: {err}")
    await interaction.followup.send(content="Не удалось", ephemeral=True)

# -- map_change
@observer.subscribe(Event.BC_CS_MAP_CHANGE)
@require_connection
async def cmd_map_change(data):
  interaction: discord.Interaction = data[Param.Interaction]
  caller_name: str = interaction.user.display_name
  mapname: str = data['map']

  command = f"ultrahc_ds_change_map {mapname}"
  
  try:
    await cs_server.exec(command)

    logger.info(f"CS Server: {caller_name} сменил карту на {mapname}")

    snd = f"```ansi\n{Color.Blue}{caller_name}{Color.Default} сменил карту на {Color.Blue}{mapname}{Color.Default}```"
    await interaction.channel.send(content=snd)
    await interaction.delete_original_response()
  except CommandExecutionError as err:
    logger.error(f"CS Server: {err}")
    await interaction.followup.send(content="Не удалось сменить карту", ephemeral=True)

# !SECTION