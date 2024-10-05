import discord.ext.tasks
from observer.observer_client import logger, observer, Event, Param, nsroute

import discord
import discord.ext
import asyncio

from bot.bot_server import dbot

import config

bot = dbot.bot

# -- on_ready
@bot.event
async def on_ready():
  logger.info(f"DBot {bot.user.name} запущен")
  
  await observer.notify(Event.BE_READY)

# -- on_message
@bot.event
async def on_message(message: discord.Message):
  if message.author == bot.user:
    return
  
  if message.channel.id == config.CS_CHAT_CHNL_ID:
    await observer.notify(Event.BE_MESSAGE, {
      Param.Message: message
    })

  await bot.process_commands(message)

# -- on_member_update
@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
  if before.display_name == after.display_name:
    return

  await observer.notify(Event.BE_MEMBER_UPDATE, {
    "user_id": after.id,
    "new_username": after.display_name
  })

# -- setup_hook
@bot.event
async def setup_hook():
  guild = bot.get_guild(config.GUILD_ID)
  await bot.tree.sync(guild=guild)

# -- (task) status_task
@discord.ext.tasks.loop(seconds=config.STATUS_INTERVAL)
async def status_task():
  await observer.notify(Event.BT_CS_Status)

# -- ev_cs_connected
@observer.subscribe(Event.CS_CONNECTED)
async def ev_cs_connected():
  if not status_task.is_running():
    status_task.start()

# -- ev_cs_disconnected
@observer.subscribe(Event.CS_DISCONNECTED)
async def ev_cs_disconnected():
  if status_task.is_running():
    status_task.cancel()

  await asyncio.sleep(10)
  await nsroute.call_route("/connect_to_cs")