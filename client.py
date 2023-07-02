import asyncio
from aiogram import types, Dispatcher
from create_bot import bot, dp, attributes
from keyboards import kb_client
from handlers.other import assign_roles, night_processing, handle_choice


async def commands_start(message : types.Message):
    # блок для отлова ошибки, когда юзер еще не начал диалог с ботом, бот не может написаь ему сам
    try:
        # пробуем написать в ЛС
        await bot.send_message(message.from_user.id, 'Добро пожаловать в игру!', reply_markup=kb_client)
    except:
        # просим юзера начать диалог
        await message.reply('Общение с ботом через ЛС, напишите ему: https://t.me/MafiaIrinaBot')


async def commands_help(message : types.Message):
    await message.reply('''Этот бот создан для игры в Мафию в чате.
    Для начала игры необходимо 3 или более участников.
    В начале игры распереляются роли случайным образом: 1 Мафия, 1 Комиссар, 1 Врач, остальные мирные жители.
    Днем возможно обсуждение в группе. Ночью голосуют мафия, врач и комиссар.
    Далее всем сообщается кто убит или никто не убит.
    Снова обсуждение и снова голосование ночью...
    Команды:
    /start - команда для начала диалога с ботом, если пользователь еще не писал боту ранее. (Пользователь должен начать диалог сам, так как в Telegram ботам запрещено писать пользователям без их согласия)
    /help - получение справочной информации
    /play - добавление пользователя в число игроков
    /new_game - начало новой игры, после этой команды новые пользователи не смогут присоединяться (/new_game должен нажать только один пользователь)
    /stop - остановка игры
    ''')


async def commands_play(message : types.Message):
    if not attributes.game_going: # если игра еще не идет, еще ждем юзеров
        if message.from_user not in attributes.players_list: # если юзер еще не в числе игроков
            await bot.send_message(message.from_user.id, 'Вы в игре! Сейчас участников: ' + str(len(attributes.players_list)+1) + '\nДавайте подождем остальных игроков...')
            attributes.players_list.append(message.from_user)
        else: # если юзер уже есть в игре
            await bot.send_message(message.from_user.id, 'Вы уже в игре')
    else:
        await bot.send_message(message.from_user.id, 'Игра уже идет, Вы не можете присоединиться.')


async def commands_new_game(message: types.Message):
    if len(attributes.players_list)<3: # если недостаточно игроков, игра не начнется
        await message.answer(f'Игра не может начаться, пока участников меньше 3-х. Сейчас игроков: {len(attributes.players_list)}')
    else:
        attributes.game_going=True
        for p in attributes.players_list:
            await bot.send_message(p.id, 'Игра началась. Сейчас будут распределены роли...')

        await asyncio.sleep(2)
        attributes.user_role_dict = assign_roles(attributes.players_list)
        for user in attributes.user_role_dict.keys():
            await bot.send_message(user.id, 'Ваша роль: ' + attributes.user_role_dict[user])

        await message.answer('Роли распределены. У вас есть 30 секунд на вопросы и обсуждение...')
        await asyncio.sleep(30)

        await night_processing(bot)


async def commands_stop(message: types.Message):
    for p in attributes.players_list:
        await bot.send_message(p.id, 'Игра остановлена.')
    attributes.players_list = []
    attributes.user_role_dict = dict()
    attributes.mafia = None
    attributes.vrach = None
    attributes.komissar = None
    attributes.mafia_picked = False
    attributes.vrach_picked = False
    attributes.komissar_picked = False
    attributes.vrach_killed = False
    attributes.game_going = False


async def catch_id(message: types.Message):
    if '@' in message.text:
        for i in message.text.strip().split():
            if i.startswith('@') and i[1:].isdigit():
                for u in attributes.user_role_dict:
                    if u.id == message.from_user.id:
                        await handle_choice(attributes.user_role_dict, i[1:], u, bot)


# рассказывает диспетчеру как обрабатывать команды
def register_handlers_client(dp : Dispatcher):
    dp.register_message_handler(commands_start, commands=['start'])
    dp.register_message_handler(commands_help, commands=['help'])
    dp.register_message_handler(commands_play, commands=['play'])
    dp.register_message_handler(commands_new_game, commands=['new_game'])
    dp.register_message_handler(commands_stop, commands=['stop'])
    dp.register_message_handler(catch_id)
