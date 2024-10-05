import logging
import traceback
import datetime

# SECTION class Log
class Log:
  # -- __init__()
  def __init__(self) -> None:
    """
    Инициализирует экземпляр класса Log и настраивает логирование.

    Создает два логгера: один для информационных сообщений, другой для сообщений об ошибках.
    """
    # INFO
    self.info_logger = logging.getLogger("LogInfo")
    self.info_logger.setLevel(logging.INFO)

    # Создаем обработчик для вывода логов в консоль
    console_handler_info = logging.StreamHandler()
    formatter_info = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    console_handler_info.setFormatter(formatter_info)
    self.info_logger.addHandler(console_handler_info)

    # Создаем обработчик для записи логов в файл
    file_handler_info = logging.FileHandler(f"logs/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_application.log", encoding='utf-8')
    file_handler_info.setFormatter(formatter_info)
    self.info_logger.addHandler(file_handler_info)

    # ERROR
    self.error_logger = logging.getLogger("LogError")
    self.error_logger.setLevel(logging.ERROR)

    # Создаем обработчик для вывода логов в консоль
    console_handler_error = logging.StreamHandler()
    formatter_error = logging.Formatter('[%(asctime)s] %(levelname)s:( %(filename)s) (%(lineno)d): %(message)s')
    console_handler_error.setFormatter(formatter_error)
    self.error_logger.addHandler(console_handler_error)
    self.error_logger.addHandler(file_handler_info)

  # -- info()
  def info(self, message: str) -> None:
    """
    Выводит информационное сообщение.

    :param message: Сообщение для вывода.
    """
    self.info_logger.info(message)

  # -- error()
  def error(self, message: str) -> None:
    """
    Выводит сообщение об ошибке.

    :param message: Сообщение об ошибке для вывода.
    """
    self.error_logger.error(message)

  # -- exception()
  def exception(self, message: str) -> None:
    """
    Выводит сообщение об исключении с трассировкой.

    :param message: Сообщение об исключении для вывода.
    """
    self.error_logger.error(f"{message}\n{traceback.format_exc()}")

# !SECTION
