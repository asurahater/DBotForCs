from observer.observer_client import nsroute, observer, Event
import discord

cache_online_players: set = {}

@observer.subscribe(Event.WBH_INFO)
async def ev_online_players(data):
  global cache_online_players
  cache_online_players = set(player['name'] for player in data['current_players'])

async def players_online(interaction: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
  global cache_online_players
  filter_players = [player_name for player_name in cache_online_players if current.lower() in player_name.lower()][:25]
  return [discord.app_commands.Choice(name=player, value=player) for player in filter_players]

async def ban_online(interaction: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
  global cache_online_players
  filter_players = [player_name for player_name in cache_online_players if current.lower() in player_name.lower()][:25] 
  return [discord.app_commands.Choice(name=player, value=player) for player in filter_players]

async def ban_offline(interaction: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
  global cache_online_players
  offline_players = (await nsroute.call_route("/redis/get_offline_players"))
  offline_set = set(offline_players)
  filtered_offline_players = list(offline_set - cache_online_players)
  filter_players = [player_name for player_name in filtered_offline_players if current.lower() in player_name.lower()][:25] 
  return [discord.app_commands.Choice(name=player, value=player) for player in filter_players]

async def ban_minutes(interaction: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
  return [
						discord.app_commands.Choice(name="5 минут",  value=5),
						discord.app_commands.Choice(name="30 минут", value=30),
						discord.app_commands.Choice(name="60 минут", value=60),
						discord.app_commands.Choice(name="1 день",   value=1440),
						discord.app_commands.Choice(name="1 неделя", value=10080),
						discord.app_commands.Choice(name="Навсегда", value=0)
				]

async def unban(interaction: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
  banned_players = (await nsroute.call_route("/redis/get_banned_players"))
  filter_players = [player_name for player_name in banned_players if current.lower() in player_name.lower()][:25] 
  return [discord.app_commands.Choice(name=player, value=player) for player in filter_players]

async def maps_active(interaction: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
  map_list = (await nsroute.call_route("/redis/get_map_list_active"))
  filter_maps = [map_name for map_name in map_list if current.lower() in map_name.lower()][:25]
  return [discord.app_commands.Choice(name=map, value=map) for map in filter_maps]

async def maps_all(interaction: discord.Interaction, current: str) -> list[discord.app_commands.Choice[str]]:
  map_list = (await nsroute.call_route("/redis/get_map_list_all"))
  filter_maps = [map_name for map_name in map_list if current.lower() in map_name.lower()][:25]
  return [discord.app_commands.Choice(name=map, value=map) for map in filter_maps]

