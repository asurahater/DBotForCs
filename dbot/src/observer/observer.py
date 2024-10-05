import asyncio
from enum import Enum
from typing import Callable, Dict, List

class Param(Enum):
  Interaction = "interaction",
  Message = "message"

class Event(Enum):
  # CS events
  CS_CONNECTED = "cs_connected"
  CS_DISCONNECTED = "cs_disconnected"

  # WebHook events
  WBH_INFO = "wbh_info"
  WBH_MESSAGE = "wbh_message"

  # Bot events
  BE_READY = "be_ready"
  BE_MESSAGE = "be_message"
  BE_MEMBER_UPDATE = "be_member_update"

  # Bot tasks
  BT_CS_Status = "bt_cs_status"

  # Bot command events
  BC_PING = "bc_ping"

  BC_CLEAR = "bc_clear"
  BC_REG = "bc_reg"
  BC_UNREG = "bc_unreg"
  BC_CONNECT_TO_CS = "bc_conncs"

  BC_DB_MAP_ADD = "bc_db_map_add"
  BC_DB_MAP_DELETE = "bc_db_map_delete"
  BC_DB_MAP_UPDATE = "bc_db_map_update"

  BC_CS_SYNC_MAPS = "bc_cs_sync_maps"
  BC_CS_RCON = "bc_cs_rcon"
  BC_CS_KICK = "bc_cs_kick"
  BC_CS_BAN = "bc_cs_ban"
  BC_CS_BAN_OFFLINE = "bc_cs_ban_offline"
  BC_CS_UNBAN = "bc_cs_unban"
  BC_CS_MAP_CHANGE = "bc_cs_map_change"


# SECTION Observer
class Observer:
  def __init__(self) -> None:
    """Инициализация наблюдателя с пустым списком подписчиков."""
    self._subscribers: Dict[str, List[Callable]] = {}

  def subscribe(self, event: Event) -> Callable:
    """Декоратор для подписки на событие.

    Args:
      event (Event): Название события, на которое подписывается пользователь.

    Returns:
      Callable: Функция обратного вызова, которая будет зарегистрирована.
    """
    def decorator(callback: Callable) -> Callable:
      if event.value not in self._subscribers:
        self._subscribers[event.value] = []
      self._subscribers[event.value].append(callback)
      return callback
    return decorator

  async def notify(self, event: Event, *args, **kwargs) -> None:
    """Уведомление всех подписчиков о событии.

    Args:
      event (Event): Название события, о котором нужно уведомить подписчиков.
      *args: Аргументы, которые будут переданы в функции обратного вызова.
      **kwargs: Ключевые аргументы, которые будут переданы в функции обратного вызова.
    """
    if event.value in self._subscribers:
      for callback in self._subscribers[event.value]:
        await asyncio.sleep(0)  # Позволяет другим задачам выполняться
        await callback(*args, **kwargs) 

# !SECTION

# SECTION NoServerRoute

class NoServerRoute:
  def __init__(self) -> None:
    self._routes: Dict[str, Callable] = {}

  def create_route(self, route: str) -> Callable:

    def decorator(callback: Callable) -> Callable:
      self._routes[route] = callback
      return callback
    
    return decorator
  
  def call_route(self, route: str, *argc, **kwargs):
    if not route in self._routes:
      return None
    
    return self._routes[route](*argc, **kwargs)


# !SECTION

# # Пример использования
# async def main():
#   observer = Observer()

#   @observer.subscribe(Event.MY_EVENT)
#   def on_event(data):
#     print(f"Получено событие с данными: {data}")

#   await observer.notify(Event.MY_EVENT, {"key": "value"})

# # Запуск примера
# asyncio.run(main())
