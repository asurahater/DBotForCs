from observer.observer import Observer, Event, Param, NoServerRoute
from logger.log import Log

class TextStyle:
  """ANSI Codes for Text Styles"""
  Default = "\x1b[0m"  # Сбрасывает все виды форматирования (включая цвет)
  Bold = "\x1b[1m"  # Жирный текст
  Underline = "\x1b[4m"  # Подчеркивающий текст
  Italic = "\x1b[3m"  # Курсивный текст
  Blink = "\x1b[5m"  # Мигающий текст
  Reverse = "\x1b[7m"  # Инвертированный цвет текста и фона

class Color:
  """ANSI Codes for Colors"""
  Default = '\x1b[0m'  # Сбрасывает цвет
  Black = '\x1b[30m'  # Черный
  Red = '\x1b[31m'  # Красный
  Green = '\x1b[32m'  # Зеленый
  Yellow = '\x1b[33m'  # Желтый
  Blue = '\x1b[34m'  # Синий
  Magenta = '\x1b[35m'  # Магента
  Cyan = '\x1b[36m'  # Циан
  White = '\x1b[37m'  # Белый

  # Яркие цвета
  Bright_Black = '\x1b[90m'  # Яркий черный (серый)
  Bright_Red = '\x1b[91m'  # Яркий красный
  Bright_Green = '\x1b[92m'  # Яркий зеленый
  Bright_Yellow = '\x1b[93m'  # Яркий желтый
  Bright_Blue = '\x1b[94m'  # Яркий синий
  Bright_Magenta = '\x1b[95m'  # Яркая магента
  Bright_Cyan = '\x1b[96m'  # Яркий циан
  Bright_White = '\x1b[97m'  # Яркий белый


# -- Init Objects
logger: Log = Log()
observer: Observer = Observer()
nsroute: NoServerRoute = NoServerRoute()