import config

from observer.observer_client import logger

from bot.bot_server import dbot

import bot.commands
import bot.events

import webserver.ws_client

import data_server.redis_server
import data_server.sql_server

import cs_server.cs_server

app_info = {
  'name': 'Ultra disBot',
  'version': '0.3',
  'author': 'Asura',
  'description': 'Bot for connecting discord and cs server'
}

if __name__ == "__main__":
  logger.info("==================================")
  logger.info(f"=== {app_info['name']} {app_info['version']}v by {app_info['author']} ===")
  logger.info("==================================")

  dbot.run()