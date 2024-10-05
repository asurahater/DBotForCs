from enum import Enum
from observer.observer_client import logger, observer, Event, nsroute, Color, TextStyle
from webserver.web_server import WebServer, WebServerError

from aiohttp import web

from datetime import datetime
import config

# -- init
ws: WebServer = WebServer(host=config.WEB_HOST_ADDRESS,
                          port=config.WEB_SERVER_PORT,
                          allowed_ips=config.CS_HOST)

# -- Events
@observer.subscribe(Event.BE_READY)
async def run_ws():
  try:
    await ws.run_webserver()
    logger.info(f"WebServer: Сервер запущен на {ws.host}:{ws.port}")
  except Exception as err:
    logger.error(err)
  

# SECTION Utilities

# -- format_message
def format_message(nick, cs_message, team, channel_prefix):
  timestamp = datetime.now().strftime('%H:%M:%S')
    
  if team == 1:
    nick_color = Color.Red
  elif team == 2:
    nick_color = Color.Blue
  else:
    nick_color = Color.White

  return f"{Color.Green}{timestamp}{Color.Default} {channel_prefix} {nick_color}{nick}{Color.Default}: {cs_message}\n"

# -- format_info_message
def format_info_message(map_name, current_players, max_players):
  player_count = len(current_players)
  team_players = {1: [], 2: [], 3: []}

  for player in current_players:
    player_name = player['name']
    stats = player['stats']
    frags = stats[0]
    deaths = stats[1]
    team = stats[2]

    if team in team_players:
      team_players[team].append(f"{player_name} - {frags}/{deaths}")
    else: # По идее это UNASSIGNED, суем в спектров
      team_players[3].append(f"{player_name} - {frags}/{deaths}")

  formatted_info = []
  formatted_info.append(f"Время: {datetime.now().strftime('%H:%M')}")
  formatted_info.append(f"Название карты: {map_name}")
  formatted_info.append(f"Количество игроков: {player_count} / {max_players}")

  if team_players[1]:
    formatted_info.append(f"\n{TextStyle.Bold}{Color.Red}Terrorists:{TextStyle.Default}")
    formatted_info.append("\n".join(f"\t{player}" for player in team_players[1]))

  if team_players[2]:
    formatted_info.append(f"\n{TextStyle.Bold}{Color.Blue}Counter-Terrorists:{TextStyle.Default}")
    formatted_info.append("\n".join(f"\t{player}" for player in team_players[2]))

  if team_players[3]:
    formatted_info.append(f"\n{TextStyle.Bold}{Color.White}Spectators:{TextStyle.Default}")
    formatted_info.append("\n".join(f"\t{player}" for player in team_players[3]))

  return "\n".join(formatted_info)

# -- check_api_key
def check_api_key(request):
  api_key = request.headers.get('Authorization') 
  if api_key == config.API_KEY:
    return True
  else:
    logger.info(f"Неверный API-ключ")
    return False

# !SECTION

# SECTION Web Hooks

# -- handle_message
async def handle_message(data: dict):

  cs_message = data['message']
  nick = data['nick']
  team = data['team']
  channel_prefix = data.get('channel', '')
  steam_id = data.get('steam_id', '')

  if not (cs_message and nick and team is not None ):
    return
  
  discord_id: int = await nsroute.call_route("/CheckSteam", steam_id=steam_id)
  prefix = ""

  if discord_id:
    member = await nsroute.call_route("/GetMember", discord_id=discord_id)
    if member:
      prefix = f"[{member.display_name}] "

  formatted_message = format_message(nick, cs_message, team, prefix + channel_prefix)

  await observer.notify(Event.WBH_MESSAGE, {
    "message": formatted_message
  })

# -- handle_info
async def handle_info(data):
  map_name = data.get('map')
  current_players = data.get('current_players', [])
  max_players = data.get('max_players')

  formatted_info = format_info_message(map_name, current_players, max_players)

  await observer.notify(Event.WBH_INFO, {
    "info_message": formatted_info,
    "current_players": current_players
  })

# !SECTION

# SECTION class WebHooksType
class WebHooksType(Enum):
  Message = 'message'
  Info = 'info'

  # Deprecated
  # Notify = 'notify' 

# !SECTION

# -- handle_webhook
async def handle_webhook(request: web.Request):
  if not check_api_key(request):
    return web.Response(text='Unauthorized', status=401)
  
  data: dict = await request.json()
  message_type: str = data['type']

  if message_type == WebHooksType.Message.value:
    await handle_message(data)
  elif message_type == WebHooksType.Info.value:
    await handle_info(data)

  return web.Response(text='OK')

# -- webhook route
ws.add_post('/webhook', handle_webhook)