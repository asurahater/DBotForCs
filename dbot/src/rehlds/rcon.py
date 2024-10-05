from io import BytesIO
from typing import Optional
import socket

startBytes = b'\xFF\xFF\xFF\xFF'
endBytes = b'\n'
packetSize = 8192

# SECTION Исключения RCON
# -- RCONError
class RCONError(Exception):
  """Базовый класс для исключений RCON."""
  pass

# -- BadRCONPassword
class BadRCONPassword(RCONError):
  """Исключение для неверного пароля RCON."""
  pass

# -- BadConnection
class BadConnection(RCONError):
  """Исключение для ошибок соединения."""
  pass

# -- ServerOffline
class ServerOffline(RCONError):
  """Исключение для оффлайн сервера."""
  pass

# -- NoConnection
class NoConnection(RCONError):
  """Исключение для отсутствия соединения."""
  pass

# !SECTION

# SECTION Class RCON
class RCON:
  # -- __init__()
  def __init__(self, *, host: str, port: int = 27015, password: str):
    """
    Инициализация класса RCON.

    :param host: Адрес хоста сервера.
    :param port: Порт сервера (по умолчанию 27015).
    :param password: Пароль для RCON.
    """
    self.host: str = host
    self.port: int = port
    self.password: str = password
    self.sock: Optional[socket.socket] = None

  # -- connect()
  def connect(self, timeout: int = 6) -> None:
    """
    Подключение к RCON серверу.

    :param timeout: Время ожидания подключения в секундах.
    :raises BadConnection: Если подключение не удалось.
    :raises BadRCONPassword: Если неверный пароль RCON.
    """
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.sock.settimeout(timeout)

    try:
      self.sock.connect((self.host, int(self.port)))
      if self.execute('stats') == 'Bad rcon_password.':
        raise BadRCONPassword("Неверный пароль RCON.")
    except Exception as e:
      self.disconnect()
      raise BadConnection(f"Ошибка при соединении с RCON: {str(e)}")

  # -- disconnect()
  def disconnect(self) -> None:
    """Отключение от RCON сервера."""
    if self.sock:
      self.sock.close()
      self.sock = None

  # -- getChallenge()
  def getChallenge(self) -> str:
    """
    Получение вызова (challenge) от сервера.

    :return: Строка вызова.
    :raises NoConnection: Если нет соединения.
    :raises ServerOffline: Если сервер оффлайн.
    """
    if not self.sock:
      raise NoConnection("Нет соединения с RCON.")

    try:
      msg = BytesIO()
      msg.write(startBytes)
      msg.write(b'getchallenge')
      msg.write(endBytes)
      self.sock.send(msg.getvalue())

      response = BytesIO(self.sock.recv(packetSize))
      return str(response.getvalue()).split(" ")[1]
    except Exception as e:
      self.disconnect()
      raise ServerOffline(f"Ошибка в getChallenge (RCON) (Возможно, сервер оффлайн): {str(e)}")

  # -- execute()
  def execute(self, cmd: str) -> str:
    """
    Выполнение команды на сервере.

    :param cmd: Команда для выполнения.
    :return: Результат выполнения команды.
    :raises ServerOffline: Если сервер оффлайн.
    """
    try:
      challenge = self.getChallenge()

      msg = BytesIO()
      msg.write(startBytes)
      msg.write(b'rcon ')
      msg.write(challenge.encode())
      msg.write(b' ')
      msg.write(self.password.encode())
      msg.write(b' ')
      msg.write(cmd.encode())
      msg.write(endBytes)

      self.sock.send(msg.getvalue())
      response = BytesIO(self.sock.recv(packetSize))

      return response.getvalue()[5:-3].decode()
    except Exception as e:
      self.disconnect()
      raise ServerOffline(f"Ошибка в execute (RCON) (Возможно, сервер оффлайн): {str(e)}")

# !SECTION
