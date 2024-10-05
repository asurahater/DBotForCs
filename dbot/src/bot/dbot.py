import discord
from discord.ext import commands

# SECTION DBot
class DBot:
  # -- __init__()
  def __init__(self, token: str):
    """
    Инициализация класса DBot.
    """
    self.token: str = token

    # Настройка интентов для бота
    self.intents: discord.Intents = discord.Intents.default()
    self.intents.message_content = True  # Позволяет получать содержимое сообщений
    self.intents.members = True  # Позволяет получать информацию о членах сервера

    # Создание экземпляра бота с заданным префиксом команд и интентами
    self.bot: commands.Bot = commands.Bot(command_prefix='/', intents=self.intents)

    # -- on_command_error()
    @self.bot.event
    async def on_command_error(ctx: commands.Context, error: Exception):
      """
      Обработчик ошибок команд.
      """
      # Проверка на ошибку, если команда не найдена
      if isinstance(error, commands.CommandNotFound):
        await ctx.send("Команда не найдена.")
      # Проверка на ошибку, если не хватает обязательных аргументов
      elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Недостаточно аргументов для этой команды.")
      # Обработка других ошибок
      else:
        await ctx.send("Произошла ошибка при выполнении команды.")

  # -- run()
  def run(self) -> None:
    """
    Запуск бота.

    Запускает цикл событий бота с использованием токена.
    """
    self.bot.run(self.token)

# !SECTION