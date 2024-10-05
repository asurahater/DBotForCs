import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Добавляем путь к папке src в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from components.cs_server import CSServer, ConnectionError, StatusError, CommandExecutionError

class TestCSServer(unittest.IsolatedAsyncioTestCase):

  def setUp(self):
    self.host = "localhost"
    self.password = "password"
    self.server = CSServer(self.host, self.password)

  @patch('rehlds.rcon.RCON')
  async def test_connect_to_server_success(self, mock_rcon):
    mock_rcon.return_value.connect = MagicMock()
    self.server.cs_server = mock_rcon.return_value

    try:
      await self.server.connect_to_server()
    except ConnectionError:
      self.fail("connect_to_server raised ConnectionError unexpectedly!")

  @patch('rehlds.rcon.RCON')
  async def test_connect_to_server_failure(self, mock_rcon):
    mock_rcon.return_value.connect.side_effect = Exception("Connection failed")
    self.server.cs_server = mock_rcon.return_value

    with self.assertRaises(ConnectionError) as context:
      await self.server.connect_to_server()
    self.assertEqual(str(context.exception), "Ошибка подключения: Connection failed")

  @patch('rehlds.rcon.RCON')
  async def test_fetch_status_success(self, mock_rcon):
    mock_rcon.return_value.execute = MagicMock()
    self.server.cs_server = mock_rcon.return_value

    try:
      await self.server.fetch_status()
    except StatusError:
      self.fail("fetch_status raised StatusError unexpectedly!")

  @patch('rehlds.rcon.RCON')
  async def test_fetch_status_failure(self, mock_rcon):
    mock_rcon.return_value.execute.side_effect = Exception("Status fetch failed")
    self.server.cs_server = mock_rcon.return_value

    with self.assertRaises(StatusError) as context:
      await self.server.fetch_status()
    self.assertEqual(str(context.exception), "Ошибка получения статуса: Status fetch failed")

  @patch('rehlds.rcon.RCON')
  async def test_exec_success(self, mock_rcon):
    mock_rcon.return_value.execute = MagicMock()
    self.server.cs_server = mock_rcon.return_value

    try:
      await self.server.exec("some_command")
    except CommandExecutionError:
      self.fail("exec raised CommandExecutionError unexpectedly!")

  @patch('rehlds.rcon.RCON')
  async def test_exec_failure(self, mock_rcon):
    mock_rcon.return_value.execute.side_effect = Exception("Command execution failed")
    self.server.cs_server = mock_rcon.return_value

    with self.assertRaises(CommandExecutionError) as context:
      await self.server.exec("some_command")
    self.assertEqual(str(context.exception), "Ошибка выполнения команды: Command execution failed")

import asyncio

async def real_test():
    cs_server = CSServer("127.0.0.1", "12345")
    await cs_server.connect_to_server()
    result = await cs_server.exec("meta list")
    await cs_server.fetch_status()
    print(result)

if __name__ == '__main__':
    # unittest.main()
    asyncio.run(real_test())