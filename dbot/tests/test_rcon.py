import sys
import os
import unittest
import asyncio

# Добавляем путь к папке src в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from rehlds.rcon import RCON  # type: ignore # Импортируем класс RCON

class TestRCON(unittest.IsolatedAsyncioTestCase):
  async def asyncSetUp(self):
    """Настройка перед каждым тестом."""
    self.host = '127.0.0.1'  # Замените на адрес вашего RCON сервера
    self.port = 27015         # Замените на порт вашего RCON сервера
    self.password = '12345'  # Замените на ваш RCON пароль
    self.rcon = RCON(host=self.host, port=self.port, password=self.password)

  async def test_connect_and_execute_command(self):
    """Тест подключения и выполнения команды."""
    self.rcon.connect()
    response = self.rcon.execute('changelevel de_dust2')  # Замените на команду, которую хотите протестировать
    print(response)  # Выводим ответ для проверки
    self.assertIsInstance(response, str)  # Проверяем, что ответ - строка

  async def asyncTearDown(self):
    """Очистка после каждого теста."""
    self.rcon.disconnect()

if __name__ == '__main__':
  unittest.main()
