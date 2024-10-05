import unittest
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

import sys
import os

# Добавляем путь к папке src в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from components.web_server import WebServer, AllowedIPsEmpty, ServerSetupFailed, ServerStartFailed  # type: ignore

async def example_handler(request: web.Request) -> web.Response:
  return web.Response(text="Hello, world!")

class TestWebServer(AioHTTPTestCase):
  async def get_application(self):
    """Создает экземпляр WebServer для тестирования."""
    self.allowed_ips = ['127.0.0.1']
    self.web_server = WebServer(host='127.0.0.1', port=8080, allowed_ips=self.allowed_ips)
    
    # Добавляем маршрут здесь, чтобы избежать ошибки "Cannot register a resource into frozen router"
    self.web_server.add_route('/test', example_handler)
    
    return self.web_server.app

  @unittest_run_loop
  async def test_initialization_with_empty_allowed_ips(self):
    """Тест на инициализацию с пустым списком разрешенных IP-адресов."""
    with self.assertRaises(AllowedIPsEmpty):
      WebServer(host='127.0.0.1', port=8080, allowed_ips=[])

  @unittest_run_loop
  async def test_initialization_with_invalid_port(self):
    """Тест на инициализацию с недопустимым портом."""
    with self.assertRaises(ServerSetupFailed):
      WebServer(host='127.0.0.1', port=0, allowed_ips=self.allowed_ips)  # Порт 0 недопустим
    with self.assertRaises(ServerSetupFailed):
      WebServer(host='127.0.0.1', port=70000, allowed_ips=self.allowed_ips)  # Порт больше 65535 недопустим

  @unittest_run_loop
  async def test_ip_check_middleware_allowed_ip(self):
    """Тест на разрешенный IP-адрес."""
    response = await self.client.request('GET', '/test')
    self.assertEqual(response.status, 200)
    self.assertEqual(await response.text(), 'Hello, world!')  # Исправлено на 'Hello, world!'

  @unittest_run_loop
  async def test_ip_check_middleware_denied_ip(self):
    """Тест на запрещенный IP-адрес."""
    # Создаем тестовый клиент
    self.web_server.allowed_ips = []  # Убираем все разрешенные IP
    app = self.web_server.app
    
    # Отправляем запрос с запрещенным IP
    response = await self.client.request('GET', '/test')
    self.assertEqual(response.status, 403)
    self.assertEqual(await response.text(), 'Access Forbidden: Your IP is not allowed.')

  @unittest_run_loop
  async def test_run_webserver_setup_failure(self):
    """Тест на ошибку при настройке сервера."""
    self.web_server.host = None  # Установим недопустимый хост
    with self.assertRaises(ServerSetupFailed):
      await self.web_server.run_webserver()  # Вызов метода для проверки

  @unittest_run_loop
  async def test_run_webserver_start_failure(self):
    """Тест на ошибку при запуске сервера с недопустимым портом."""
    self.web_server.port = 99999  # Установим недопустимый порт
    with self.assertRaises(ServerStartFailed):
      await self.web_server.run_webserver()  # Вызов метода для проверки

  @unittest_run_loop
  async def test_successful_server_start(self):
    """Тест на успешный запуск сервера."""
    try:
      await self.web_server.run_webserver()  # Попытка запуска сервера
      self.assertTrue(True)  # Если не возникло исключений, тест пройден
    except Exception:
      self.fail("Server failed to start with valid parameters.")

if __name__ == '__main__':
  unittest.main()
