from rehlds.rcon import RCON
from typing import Optional
from enum import Enum

# SECTION Исключения CSServer

# -- CSServerError
class CSServerError(Exception):
  """Базовый класс для исключений CSServer."""
  pass

# -- ServerNotConnected
class ServerNotConnected(CSServerError):
  """Исключение для случая, когда сервер не подключен."""
  pass

# -- ConnectionError
class ConnectionError(CSServerError):
  """Исключение для ошибок подключения к серверу."""
  pass

# -- StatusError
class StatusError(CSServerError):
  """Исключение для ошибок при получении статуса сервера."""
  pass

# -- CommandExecutionError
class CommandExecutionError(CSServerError):
  """Исключение для ошибок при выполнении команды на сервере."""
  pass

# !SECTION

class DefaultCommands(Enum):
    GET_STATUS = "ultrahc_ds_get_info"

# SECTION Class CSRCON
class CSRCON:
  # -- __init__()
  def __init__(self, host: str, password: str) -> None:
    """
    Инициализирует экземпляр CSServer.

    :param host: Адрес сервера.
    :param password: Пароль для подключения к серверу.
    """
    self.cs_server: RCON = RCON(host=host, password=password)
    self.connected: bool = False

  # -- connect_to_server()
  async def connect_to_server(self) -> None:
    """
    Подключается к серверу CS и возвращает статус.
    
    :raises ConnectionError: Если не удалось подключиться к серверу.
    """
    try:
      self.cs_server.connect()
      self.connected = True
    except Exception as e:
      raise ConnectionError(f"Ошибка подключения: {str(e)}")
    
  # -- disconnect()
  async def disconnect(self) -> None:
    """
    Отключается от сервера кс
    """
    self.cs_server.disconnect()
    self.connected = False

  # -- fetch_status()
  async def fetch_status(self) -> None:
    """
    Получает статус сервера и возвращает статус.

    :raises ServerNotConnected: Если сервер не подключен.
    :raises StatusError: Если произошла ошибка при получении статуса сервера.
    """

    try:
      self.cs_server.execute(DefaultCommands.GET_STATUS.value)
    except Exception as e:
      raise StatusError(f"Ошибка получения статуса: {str(e)}")

  # -- exec()
  async def exec(self, command: str) -> str:
    """
    Выполняет команду на сервере.

    :param command: Команда для выполнения.
    :raises CommandExecutionError: Если произошла ошибка при выполнении команды.
    """
    try:
      return self.cs_server.execute(command)
    except Exception as e:
      raise CommandExecutionError(f"Ошибка выполнения команды: {str(e)}")

# !SECTION
