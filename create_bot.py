from aiogram import Bot # импортируем из aiogram класс бота
from aiogram.dispatcher import Dispatcher # импортируем из aiogram класс диспетчера
from aiogram.contrib.fsm_storage.memory import MemoryStorage # импортируем из aiogram память, в которой будут храниться наши данные
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# создали объект памяти
storage = MemoryStorage()

# создали объект класса Бот, передали токен
bot = Bot("5684246265:AAHYkPO0aMx6wAOxgdNem98psmE89XXjMsM")
# создали объект класса Диспетчер
dp = Dispatcher(bot, storage=storage)

# класс, в котором мы храним необходимую для игры информацию
class Attributes:
    def __init__(self):
        self.players_list = [] # список игроков (юзеров)
        self.user_role_dict = dict() # словарь игроков Юзер : Роль

        # юзеры главных героев
        self.mafia=None
        self.vrach=None
        self.komissar=None

        # сделали ли герои выбор
        # False заменяется на Юзера выбранного игрока
        self.mafia_picked=False
        self.vrach_picked=False
        self.komissar_picked=False

        # флаг, что врача убили, чтобы не ждать его выбора
        self.vrach_killed=False

        # флаг, что игра идет, чтобы не добавлять новых юзеров
        self.game_going = False

# создали объект класса атрибуты
attributes = Attributes()