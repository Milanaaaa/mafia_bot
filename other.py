import random
import asyncio
from create_bot import attributes, bot
# from create_bot import user_role_dict


def assign_roles(players_list):
    roles_list = ['Мафия', 'Комиссар', 'Врач']
    if len(players_list) > len(roles_list):
        roles_list += ['Мирный житель'] * (len(players_list) - 3)
    random.shuffle(roles_list)

    user_role_dict = dict()
    for i in range(len(players_list)):
        user_role_dict[players_list[i]] = roles_list[i]
        if roles_list[i]=='Мафия':
            attributes.mafia=players_list[i]
        elif roles_list[i]=='Врач':
            attributes.vrach=players_list[i]
        elif roles_list[i]=='Комиссар':
            attributes.komissar=players_list[i]

    attributes.user_role_dict = user_role_dict
    return user_role_dict

async def night_processing(bot):
    for user in attributes.user_role_dict.keys():
        await bot.send_message(user.id, 'Город засыпает...')

        if attributes.user_role_dict[user] == 'Мафия':
            active_players_text = await get_active_players_list(user, attributes.user_role_dict)
            await bot.send_message(user.id, 'Просыпается Мафия.')
            await bot.send_message(user.id, 'Напишите id жертвы:\n' + active_players_text)
        elif attributes.user_role_dict[user] == 'Комиссар':
            active_players_text = await get_active_players_list(user, attributes.user_role_dict)
            await bot.send_message(user.id, 'Просыпается Комиссар.')
            await bot.send_message(user.id, 'Напишите id предполагаемой мафии:\n' + active_players_text)
        elif attributes.user_role_dict[user] == 'Врач':
            active_players_text = await get_active_players_list(user, attributes.user_role_dict)
            await bot.send_message(user.id, 'Просыпается Врач.')
            await bot.send_message(user.id, 'Напишите id того, кого хотите вылечить:\n' + active_players_text)



async def results(bot):
    if attributes.mafia_picked and (attributes.vrach_picked or attributes.vrach_killed) and attributes.komissar_picked:
        for p in attributes.players_list:
            await bot.send_message(p.id, 'Город просыпается.')

            if attributes.komissar_picked == attributes.mafia:
                await bot.send_message(p.id, f'Игра окончена. Комиссар {attributes.komissar.first_name} поймал Мафию {attributes.mafia.first_name}. Мирные жители победили!')
                attributes.game_going = False
            elif attributes.vrach_picked == attributes.mafia_picked:
                await bot.send_message(p.id, 'Врач вылечил жертву Мафии. Сегодня никто не пострадал.')
            else:
                if p == attributes.mafia_picked:
                    await bot.send_message(p.id, f'Сегодняшней ночью Вас убила Мафия...')
                else:
                    await bot.send_message(p.id, f'Сегодня убили {attributes.mafia_picked.first_name}...')

                if attributes.user_role_dict[attributes.mafia_picked] == 'Врач':
                    attributes.vrach_killed=True
                attributes.user_role_dict[attributes.mafia_picked] = 'Killed'

                alive=0
                for u in attributes.user_role_dict:
                    if attributes.user_role_dict[u] != 'Killed':
                        alive+=1
                await bot.send_message(p.id, f'В городе осталось вживых: {alive}')
                if alive==2 or attributes.user_role_dict[attributes.mafia_picked]=='Комиссар':
                    await bot.send_message(p.id, f'Игра окончена. Мафия {attributes.mafia.first_name} победила.')
                    attributes.game_going=False

        if not attributes.game_going:
            attributes.players_list = []
            attributes.user_role_dict = dict()
            attributes.mafia = None
            attributes.vrach = None
            attributes.komissar = None
            attributes.mafia_picked = False
            attributes.vrach_picked = False
            attributes.komissar_picked = False
            attributes.game_going = False

        else:
            attributes.mafia_picked = False
            attributes.vrach_picked = False
            attributes.komissar_picked = False

            for u in attributes.user_role_dict.keys():
                if attributes.user_role_dict[u]!='Killed':
                    await bot.send_message(u.id, 'У вас есть 15 секунд на обсуждение.')
            await asyncio.sleep(15)

            await night_processing(bot)



async def get_active_players_list(receiver, user_role_dict):
    text = ''
    for user in user_role_dict.keys():
        if user_role_dict[user] != "Killed" and user!=receiver:
            text += '@' + str(user.id) + "  " + str(user.first_name) + " " + str(user.last_name) + " " + str(user.username) + "\n"
    if user_role_dict[receiver]=='Врач':
        text += '@' + str(receiver.id) + "  " + str(receiver.first_name) + " " + str(receiver.last_name) + " " + str(
            receiver.username) + "\n"
    return text


async def handle_choice(ur_dct, id_choice, chooser_user, bot):
    found_user=False # ищем юзера, которому принадлежит id
    for u in ur_dct.keys():
        if str(u.id).strip() == str(id_choice).strip() and ur_dct[u]!='Killed':
            found_user=u
            break
    if not found_user:
        await bot.send_message(chooser_user.id, 'Такого участника в игре нет.')
    else:
        if ur_dct[chooser_user]=='Мафия':
            if attributes.mafia_picked:
                await bot.send_message(chooser_user.id, 'Вы уже сделали выбор ранее.')
            else:
                attributes.mafia_picked=found_user
                await bot.send_message(chooser_user.id, 'Вы сделали выбор.')

        elif ur_dct[chooser_user]=='Врач':
            if attributes.vrach_picked:
                await bot.send_message(chooser_user.id, 'Вы уже сделали выбор ранее.')
            else:
                attributes.vrach_picked=found_user
                await bot.send_message(chooser_user.id, 'Вы сделали выбор.')

        elif ur_dct[chooser_user]=='Комиссар':
            if attributes.komissar_picked:
                await bot.send_message(chooser_user.id, 'Вы уже сделали выбор ранее.')
            else:
                attributes.komissar_picked=found_user
                await bot.send_message(chooser_user.id, 'Вы сделали выбор.')
    if attributes.mafia_picked and attributes.komissar_picked and (attributes.vrach_picked or attributes.vrach_killed):
        await results(bot)

