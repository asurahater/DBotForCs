import unittest
from unittest.mock import patch, MagicMock
import logging
import traceback

import sys
import os

# Добавляем путь к папке src в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Предполагаем, что класс Log находится в файле log_module.py
from components.log import Log  # type: ignore

class TestLog(unittest.TestCase):

  @patch('logging.getLogger')
  def setUp(self, mock_get_logger):
    # Создаем мок-логгеры
    self.mock_info_logger = MagicMock()
    self.mock_error_logger = MagicMock()
    
    # Настраиваем mock для логгеров
    mock_get_logger.side_effect = [self.mock_info_logger, self.mock_error_logger]

    # Создаем экземпляр Log
    self.log = Log()

  def test_info_logging(self):
    message = "This is an info message"
    self.log.info(message)
    
    # Проверяем, что info_logger.info был вызван с правильным сообщением
    self.mock_info_logger.info.assert_called_once_with(message)

  def test_error_logging(self):
    message = "This is an error message"
    self.log.error(message)
    
    # Проверяем, что error_logger.error был вызван с правильным сообщением
    self.mock_error_logger.error.assert_called_once_with(message)

  @patch('traceback.format_exc')
  def test_exception_logging(self, mock_format_exc):
    message = "This is an exception message"
    mock_format_exc.return_value = "Traceback (most recent call last): ..."
    
    self.log.exception(message)
    
    # Проверяем, что error_logger.error был вызван с правильным сообщением
    self.mock_error_logger.error.assert_called_once_with(f"{message}\n{mock_format_exc.return_value}")

if __name__ == '__main__':
  unittest.main()
