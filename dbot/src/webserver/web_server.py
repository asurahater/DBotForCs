from aiohttp import web
from enum import Enum
from typing import Callable, List, Optional

from observer.observer_client import observer, Event

# SECTION Исключения WebServer

# -- WebServerError
class WebServerError(Exception):
  """Базовый класс для исключений веб-сервера."""
  pass

# -- ServerSetupFailed
class ServerSetupFailed(WebServerError):
  """Исключение для ошибок при настройке сервера."""
  pass

# -- ServerStartFailed
class ServerStartFailed(WebServerError):
  """Исключение для ошибок при запуске сервера."""
  pass

# -- AllowedIPsEmpty
class AllowedIPsEmpty(WebServerError):
  """Исключение для случая, когда список разрешенных IP-адресов пуст."""
  pass

# !SECTION

# SECTION Class WebServer
class WebServer:
  # -- __init__()
  def __init__(self, host: str, port: int, allowed_ips: List[str]) -> None:
    """
    Инициализирует экземпляр веб-сервера.

    :param host: Адрес, на котором будет запущен сервер.
    :param port: Порт, на котором будет запущен сервер.
    :param allowed_ips: Список разрешенных IP-адресов для доступа к серверу.
    """
    if not allowed_ips:
      raise AllowedIPsEmpty("allowed_ips list cannot be empty.")
    
    if port <= 0 or port > 65535:
      raise ServerSetupFailed("Port must be between 1 and 65535.")
    
    self.app: web.Application = web.Application()
    self.host: str = host
    self.port: int = port
    self.allowed_ips: List[str] = allowed_ips

    # Добавление middleware для проверки IP-адресов
    self.app.middlewares.append(self.ip_check_middleware)

  # -- ip_check_middleware()
  @web.middleware
  async def ip_check_middleware(self, request: web.Request, handler: Callable) -> web.Response:
    """
    Middleware для проверки IP-адресов клиентов.

    :param request: HTTP-запрос.
    :param handler: Функция-обработчик для обработки запроса.
    :return: Ответ на запрос или ошибка доступа.
    """
    client_ip: str = request.remote
    if client_ip not in self.allowed_ips:
      await observer.notify(Event.WS_IP_NOT_ALLOWED, {
        "request_remote": request.remote,
        "request_url": request.url,
        "request_method": request.method,
        "request_headers": request.headers,
        "request_body": await request.text()
      })
      return web.Response(status=403, text="Access Forbidden: Your IP is not allowed.")
    
    # Если IP-адрес разрешен, продолжить обработку запроса
    return await handler(request)

  # -- add_route()
  def add_post(self, path: str, handler: Callable, method: str = 'GET') -> None:
    """
    Добавляет маршрут в приложение.

    :param path: Путь маршрута.
    :param handler: Функция-обработчик для данного маршрута.
    :param method: HTTP-метод (по умолчанию 'GET').
    """
    self.app.router.add_post(path, handler)

  # -- run_webserver()
  async def run_webserver(self) -> None:
    """
    Запускает веб-сервер.
    :raises ServerSetupFailed: Ошибка при настройке сервера.
    :raises ServerStartFailed: Ошибка при запуске сервера.
    """
    if self.host is None:
      raise ServerSetupFailed("Host cannot be None.")
    
    try:
      self._runner: web.AppRunner = web.AppRunner(self.app)
      await self._runner.setup()
    except Exception as e:
      raise ServerSetupFailed(f"Ошибка при настройке сервера: {str(e)}") from e
    
    try:
      self._site: web.TCPSite = web.TCPSite(self._runner, self.host, self.port)
      await self._site.start()
    except Exception as e:
      raise ServerStartFailed(f"Ошибка при запуске сервера: {str(e)}") from e

# !SECTION
