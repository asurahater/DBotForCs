from bot.dbot import DBot
from observer.observer_client import observer, Event, logger, nsroute

import discord

import config

dbot: DBot = DBot(config.BOT_TOKEN)

cs_chat_duser_msg: bool = False
cs_chat_max_chars: int = 1000
cs_chat_last_message: discord.Message = None

cs_status_message: discord.Message = None

# SECTION Utilities

# -- concat_message
def concat_message(old_message: str, new_message: str) -> str:
  delete_closing = old_message[:-3] if old_message.endswith('```') else old_message

  return delete_closing + new_message + '```'

# -- send_message
async def send_message(message: str, channel: discord.TextChannel) -> None:
  global cs_chat_last_message, cs_chat_duser_msg

  try:
    cs_chat_last_message = await channel.send(f"```ansi\n{message}```")
    cs_chat_duser_msg = False
  except Exception as e:
    logger.error(f"Ошибка при отправке сообщения в Discord: {e}")

# -- edit_message
async def edit_message(message: str, channel: discord.TextChannel) -> None:
  global cs_chat_last_message, cs_chat_max_chars

  formatted_message = concat_message(cs_chat_last_message.content, message)

  if len(formatted_message) > cs_chat_max_chars:
    send_message(formatted_message, channel)
    return
  
  try:
    cs_chat_last_message = await cs_chat_last_message.edit(content=formatted_message)
  except Exception as e:
    logger.error(f"Dbot: Ошибка при обновлении CS_CHAT в Discord: {e}")

# -- edit_status_message
async def edit_status_message(message: str, channel: discord.TextChannel):
  global cs_status_message

  # Проверка на существование сообщения
  try:
    cs_status_message = await channel.fetch_message(cs_status_message.id)
  except discord.NotFound as err:
    cs_status_message = None
    await send_status_message(message, channel)
    return

  try:
    cs_status_message = await cs_status_message.edit(content=f"```ansi\n{message}```")
  except Exception as e:
    logger.error(f"Dbot: Ошибка при обновлении CS_STATUS в Discord: {e}")

# -- is_bot
def is_bot(message: discord.Message):
  return message.author == dbot.bot.user

# -- send_status_message
async def send_status_message(message: str, channel: discord.TextChannel):
  global cs_status_message
  await channel.purge(limit=10)

  cs_status_message = await channel.send(f"```ansi\n{message}```")

# !SECTION

# -- (route) get_member
@nsroute.create_route("/GetMember")
async def get_member(discord_id: int) -> discord.Member:
  guild = dbot.bot.get_guild(config.GUILD_ID)
  member: discord.Member 

  try:
    member = await guild.fetch_member(discord_id)
  except discord.NotFound as err:
    member = None


  return member
  
# -- ev_message
@observer.subscribe(Event.WBH_MESSAGE)
async def ev_message(data) -> None:
  global cs_chat_duser_msg
  message = data['message']

  channel = dbot.bot.get_channel(config.CS_CHAT_CHNL_ID)

  if not channel:
    logger.error("DBot: CS_CHAT_CHANNEL Не найден")
    return

  if cs_chat_duser_msg or not cs_chat_last_message:
    await send_message(message, channel)
  else:
    await edit_message(message, channel)

# -- ev_info
@observer.subscribe(Event.WBH_INFO)
async def ev_info(data) -> None:
  global cs_status_message

  info_message = data['info_message']
  channel = dbot.bot.get_channel(config.INFO_CHANNEL_ID)

  if not channel:
    logger.error("DBot: CS_INFO_CHANNEL Не найден")
    return

  if cs_status_message:
    await edit_status_message(info_message, channel)
  else:
    await send_status_message(info_message, channel)

