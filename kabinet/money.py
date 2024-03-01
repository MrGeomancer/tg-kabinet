import asyncio
from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Router, html
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton
import logging

import database

router = Router()


class Kabinet_money_state(StatesGroup):
    Kabinet_main = State()
    Kabinet_money = State()
    Kabinet_money_new_ask = State()
    Kabinet_money_new_ask_price = State()
    Kabinet_money_new_ask_count = State()
    Kabinet_money_new_ask_komment = State()
    Kabinet_money_chng_ask = State()
    Kabinet_money_chng_value = State()
    Kabinet_money_del = State()


changes_lists={'price':['цена закупки', 'цена', 'цену','стоимость','ц'],
               'description':['комментарий','коммент','описание','ком','описание'],
               'count':['кол-во','колличество','колво','количество','закуп','объем','к','кол'],
               }

changes_list=[]
for znach in changes_lists.values():
    for text in znach:
        changes_list.append(text)

changes_lists.update({"price_keys":len(changes_lists['price']),
                      "description_keys":len(changes_lists['description']),
                      "count_keys":len(changes_lists['count'])
                      })


async def take_change(index):
    if index+1 <= changes_lists['price_keys']:
        change_item = 'price'
    elif changes_lists['price_keys'] < index+1 <= changes_lists['description_keys']+changes_lists['price_keys']:
        change_item = 'description'
    elif index+1 > changes_lists['description_keys']+changes_lists['price_keys']:
        change_item = 'count'
    return change_item


@router.message(F.text == "💲  Валютные")
async def kabinet_money_main(message: Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='➕ Добавить'))
    builder.add(KeyboardButton(text='❔ Изменить'))
    builder.add(KeyboardButton(text='➖ Удалить'))
    builder.add(KeyboardButton(text='◀️ Назад'))
    builder.add(KeyboardButton(text='⭕️ Вернуться в главное меню'))
    builder.adjust(3)

    # Клавиатура для пользователей без кейсов
    builder2 = ReplyKeyboardBuilder()
    builder2.add(KeyboardButton(text='➕ Добавить'))
    builder2.add(KeyboardButton(text='◀️ Назад'))
    builder2.add(KeyboardButton(text='⭕️ Вернуться в главное меню'))
    builder2.adjust(2)
    text = await database.money_take_names_and_prices(user_id=message.from_user.id)
    # print(text)
    if text == []:
        await message.answer(text="Ты еще не добавил закупок валют в свой кабинет. Можешь добавить сейчас, нажав на "
                                  "кнопку ниже или сделать это позже на этой странице или на странице отслеживания.",
                             reply_markup=builder2.as_markup(resize_keyboard=True),
                             parse_mode=ParseMode.HTML,
                             )
    else:
        msg = ''
        for lot in text:
            # print("lot ",lot)
            msg = msg + f"\n{lot[3]}. {html.bold(lot[4])} {html.bold(lot[0])} купленные по {html.bold(lot[1])} рублей"
            # msg = msg + f'\n{lot[3]}.{html.bold(lot[0])} купленный за {html.bold(f'{lot[1]}x{lot[4]}')} рублей'
            if lot[2] is not None: msg = msg + f' (<i>{lot[2]}</i>)'
        await message.answer(text=f"Твои валютные инвестиции:{msg}.\nХочешь изменить информацию?",
                             reply_markup=builder.as_markup(resize_keyboard=True),
                             parse_mode=ParseMode.HTML,
                             )
    await state.set_state(Kabinet_money_state.Kabinet_money)


@router.message(F.text == '◀️ Назад', Kabinet_money_state())
async def kabinet_back(message: Message, state: FSMContext):
    # print('поймал команду Съебаться')
    await state.clear()
    await kabinet_money_main(message, state)


@router.message(F.text == '➕ Добавить', Kabinet_money_state.Kabinet_money)
async def kabinet_money_new(message: Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='🇺🇸 USD'))
    builder.add(KeyboardButton(text='🇪🇺 EUR'))
    builder.add(KeyboardButton(text='🇨🇳 CHY'))
    builder.add(KeyboardButton(text='🇦🇪 AED'))
    builder.add(KeyboardButton(text='🥇 GOLD'))
    builder.add(KeyboardButton(text='⭕️ Вернуться в главное меню'))
    await message.reply(text='Выбери что было тобой закуплено, нажав на кнопку снизу',
                        reply_markup=builder.as_markup(resize_keyboard=True)
                        )
    await state.set_state(Kabinet_money_state.Kabinet_money_new_ask)


@router.message(F.text, Kabinet_money_state.Kabinet_money_new_ask)
async def kabinet_money_new_ask(message: Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='◀️ Назад'))
    builder.add(KeyboardButton(text='⭕️ Вернуться в главное меню'))
    if message.text == '🇺🇸 USD':
        await message.reply(text='Доллары значит, принято')
    elif message.text == '🇪🇺 EUR':
        await message.reply(text='Евро значит, принято')
    elif message.text == '🇨🇳 CHY':
        await message.reply(text='Юани значит, принято')
    elif message.text == '🇦🇪 AED':
        await message.reply(text='Дирхамы значит, принято')
    elif message.text == '🥇 GOLD':
        await message.reply(text='Золото значит, принято, считаем в граммах')
    else:
        await message.reply('Принимаются только значения из кнопок')
        await message.answer(text='Давай ты попробуешь еще раз.')
        await kabinet_money_new(message, state)
    await message.answer(text='Сколько стоил один, когда ты их покупал?',
                         reply_markup=builder.as_markup(resize_keyboard=True))
    await state.update_data(currency=message.text.split()[1])
    await state.set_state(Kabinet_money_state.Kabinet_money_new_ask_price)


@router.message(F.text, Kabinet_money_state.Kabinet_money_new_ask_price)
async def kabinet_money_new_ask_price(message: Message, state: FSMContext):
    msg = message.text
    try:
        msg = float(msg.replace(",", "."))
        await state.update_data(price=msg)
        await message.reply(text='Окей, сколько ты их закупил?')
        await state.set_state(Kabinet_money_state.Kabinet_money_new_ask_count)
    except ValueError as e:
        logging.error(f'Error at def kabinet.money.kabinet_money_new_ask_price\n{e} ', exc_info=True)
        await message.reply('Вводи пожалуйста только цифры')
        await state.set_state(Kabinet_money_state.Kabinet_money_new_ask_price)
    except Exception as e:
        logging.error(f'Error at def kabinet.money.kabinet_money_new_ask_price\n{e}', exc_info=True)
        await message.answer(f'произошла ошибка, расскажи пожалуйста комунибудь о ней\n{e}')
        pass


@router.message(F.text, Kabinet_money_state.Kabinet_money_new_ask_count)
async def kabinet_money_new_ask_count(message: Message, state: FSMContext):
    msg = message.text
    try:
        msg = float(msg.replace(",", "."))
        await state.update_data(count=msg)
        await message.reply(text='Принято, ждем добавления...⏳')
        # await state.set_state(Ignor_user_State.Ignoring)
        user_data = await state.get_data()
        # print(user_data)
        text = await database.add_money(user_data, user_id=message.from_user.id)
        msg = (f"{text['currency']} добавлено в твою базу данных со стоимостью в {user_data['price']} рублей, в объеме {user_data['count']}."
               '\nХочешь добавить комментарий к этой закупке? '
               'Можешь написать его сообщением или, если нет, то жми на кнопку')
        await message.answer(text=msg)
        await state.set_state(Kabinet_money_state.Kabinet_money_new_ask_komment)
    except ValueError as e:
        logging.error(f'Error at def kabinet.money.kabinet_money_new_ask_price\n{e} ', exc_info=True)
        await message.reply('Вводи пожалуйста только цифры')
    except Exception as e:
        logging.error('Error at %s', 'def kabinet.kabinet_money_new_ask_count', exc_info=True)
        await message.answer(f'произошла ошибка, расскажи пожалуйста комунибудь о ней\n{e}')
        pass


@router.message(F.text, Kabinet_money_state.Kabinet_money_new_ask_komment)
async def kabinet_money_new_ask_komment(message: Message, state: FSMContext):
    await state.update_data(komment=message.text)
    await database.add_komment_money(user_data=await state.get_data(), user_id=message.from_user.id)
    await message.reply(text='Принято.')
    await state.clear()
    await kabinet_money_main(message, state)


@router.message(F.text == '❔ Изменить', Kabinet_money_state.Kabinet_money)
async def kabinet_money_change(message: Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='◀️ Назад'))
    builder.add(KeyboardButton(text='⭕️ Вернуться в главное меню'))
    await message.answer(text='Напиши в чат id закупки, информацию о которой ты хочешь изменить.'
                              '\nID пишется в начале каждой строки списка, при их выводе, в кабинете. '
                              'Через запятую после ID ты должен написать что хочешь изменить из параметров '
                              '(<u>цена закупки</u>, <u>комментарий</u>, <u>колличество</u>)'
                              f"\nПример команды: {html.bold('32, комментарий')}",
                         parse_mode=ParseMode.HTML,
                         reply_markup=builder.as_markup(resize_keyboard=True)
                         )
    await state.set_state(Kabinet_money_state.Kabinet_money_chng_ask)


@router.message(F.text, Kabinet_money_state.Kabinet_money_chng_ask)
async def kabinet_money_change_ask(message: Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='◀️ Назад'))
    builder.add(KeyboardButton(text='⭕️ Вернуться в главное меню'))
    print(message.text)
    msg = message.text.split(',')
    try: msg[1]=msg[1].strip().lower()
    except: pass
    if len(msg) > 2 or len(msg) < 2:
        print('много запятых')
        await message.reply(text='Можно передать только два параметра, разделенных запятой.\n<b>ID</b>,<b>что изменить</b>',
                            parse_mode=ParseMode.HTML,
                            reply_markup=builder.as_markup(resize_keyboard=True)
                            )
        await message.answer(text='Давай ты попробуешь еще раз.')
        await state.set_state(Kabinet_money_state.Kabinet_money_chng_ask)
    elif msg[1] not in changes_list:
        print('предложенного параметра нет в списке')
        await message.reply(text='Тебе надо отправить ID и через запяную написать что изменить, как в примере в прошлом сообщении. Используй что-то одно из (<u>название</u>, <u>цена закупки</u>, <u>комментарий</u>, <u>колличество</u>)\n<b>ID</b>,<b>что изменить</b>',
                            parse_mode=ParseMode.HTML,
                            reply_markup=builder.as_markup(resize_keyboard=True)
                            )
        await message.answer(text='Давай ты попробуешь еще раз.')
        await state.set_state(Kabinet_money_state.Kabinet_money_chng_ask)
    elif not msg[0].isdigit():
        print('id написан не цифрой')
        await message.reply(text='Тебе надо отправить числовой ID, он пишется перед названием кейса.\n<b>ID</b>,<b>что изменить</b>',
                            parse_mode=ParseMode.HTML,
                            reply_markup=builder.as_markup(resize_keyboard=True)
                            )
        await message.answer(text='Давай ты попробуешь еще раз.')
        await state.set_state(Kabinet_money_state.Kabinet_money_chng_ask)
    else:
        await state.update_data(change_moneyid=msg[0])
        change = await take_change(changes_list.index(msg[1]))
        await state.update_data(change_money_changeitem=change)
        await message.reply(text=f'Хорошо, напиши в следующем сообщении на какое значение ты хочешь поменять параметр {change}',
                            parse_mode=ParseMode.HTML,
                            reply_markup=builder.as_markup(resize_keyboard=True)
                            )
        await state.set_state(Kabinet_money_state.Kabinet_money_chng_value)

@router.message(F.text, Kabinet_money_state.Kabinet_money_chng_value)
async def kabinet_money_change_ask_value(message: Message, state: FSMContext):
    await message.reply(text='Хорошо, изменения направлены в базу, сейчас покажу что получилось')
    await state.update_data(change_money_changenew=message.text)
    user_data = await state.get_data()
    result = await database.change_smth_money(user_data, user_id=message.from_user.id)
    if result is True:
        await state.clear()
        await kabinet_money_main(message, state)
    else:
        await message.answer(text='Что-то пошло не так при изменении данных в базе...')
        await state.clear()
        await kabinet_money_main(message, state)


@router.message(F.text == '➖ Удалить', Kabinet_money_state.Kabinet_money)
async def kabinet_new(message: Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='◀️ Назад'))
    builder.add(KeyboardButton(text='⭕️ Вернуться в главное меню'))
    await message.answer(text='Напиши в чат id закупки, которую ты хочешь удалить из своей базы данных.'
                              '\nID пишется в списке перед его названием, при их выводе, в кабинете. '
                              'Через запятую после ID ты можешь написать еще несколько ID',
                         parse_mode=ParseMode.HTML,
                         reply_markup=builder.as_markup(resize_keyboard=True)
                         )
    await state.set_state(Kabinet_money_state.Kabinet_money_del)


@router.message(F.text, Kabinet_money_state.Kabinet_money_del)
async def kabinet_new(message: Message, state: FSMContext):
    msg = message.text.split(',')
    for i in range(len(msg)):
        msg[i] = msg[i].strip()
    text = await database.del_money(msg, user_id=message.from_user.id)
    await message.reply(text)
    await state.clear()
    await kabinet_money_main(message, state)
