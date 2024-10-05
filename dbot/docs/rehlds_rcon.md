# Модуль RCON

Данный модуль реализует клиент для удаленного управления серверами через RCON (Remote Console). Он поддерживает подключение к серверу, выполнение команд и обработку ошибок.

## Установка

Для использования данного модуля не требуется установка дополнительных зависимостей, так как он использует стандартные библиотеки Python.

## Классы

### RCON

Класс для создания и управления подключением к RCON серверу.

#### Атрибуты

- `host` (str): Адрес хоста сервера.
- `port` (int): Порт сервера (по умолчанию 27015).
- `password` (str): Пароль для RCON.
- `sock` (Optional[socket.socket]): Сокет для подключения к серверу.

#### Методы

- `__init__(host: str, port: int = 27015, password: str) -> None`
  - Инициализирует экземпляр класса RCON.
  - **Параметры:**
    - `host`: Адрес хоста сервера.
    - `port`: Порт сервера (по умолчанию 27015).
    - `password`: Пароль для RCON.

- `connect(timeout: int = 6) -> None`
  - Подключение к RCON серверу.
  - **Параметры:**
    - `timeout`: Время ожидания подключения в секундах.

- `disconnect() -> None`
  - Отключение от RCON сервера.

- `getChallenge() -> str`
  - Получение вызова (challenge) от сервера.
  - **Возвращает:**
    - Строка вызова.

- `execute(cmd: str) -> str`
  - Выполнение команды на сервере.
  - **Параметры:**
    - `cmd`: Команда для выполнения.
  - **Возвращает:**
    - Результат выполнения команды.

## Исключения

- `RCONError`: Базовый класс для исключений RCON.
- `BadRCONPassword`: Исключение для неверного пароля RCON.
- `BadConnection`: Исключение для ошибок соединения.
- `ServerOffline`: Исключение для оффлайн сервера.
- `NoConnection`: Исключение для отсутствия соединения.

## Лицензия

Этот проект лицензирован под MIT License.