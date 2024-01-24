import asyncio
from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Router, Bot, Dispatcher, html
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton

import config
import database

router = Router()


class Kabinet_State(StatesGroup):
    Kabinet_main = State()
    Kabinet_cases = State()
    Kabinet_cases_new_ask = State()
    Kabinet_cases_new_ask_price = State()
    Kabinet_cases_new_ask_komment = State()
    Kabinet_cases_chng_ask = State()
    Kabinet_cases_chng_value = State()

changes_lists={'name':['название','имя'],
               'price':['цена закупки', 'цена', 'цену'],
               'discription':['комментарий','коммент','описание','ком'],
               }
changes_lists.update({"name_keys":len(changes_lists['name']),
                      "price_keys":len(changes_lists['price']),
                      "discription_keys":len(changes_lists['discription'])
                      })
changes_list=[]
for i in changes_lists['name']:
    changes_list.append(i)
for i in changes_lists['price']:
    changes_list.append(i)
for i in changes_lists['discription']:
    changes_list.append(i)


async def take_change(index):
    if index+1 <= changes_lists['name_keys']:
        change_item = 'name'
    elif index+1 > changes_lists['name_keys'] and index+1 <= changes_lists['price_keys']:
        change_item = 'price'
    elif index+1 > changes_lists['price_keys'] and index+1 <= changes_lists['discription_keys']:
        change_item = 'description'
    return change_item


@router.message(F.text == "👨‍🏫 Мой кабинет")
async def kabinet_main_page(message: Message, state: FSMContext):
    print('зашел в кабинет')
    await state.clear()
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='🧰 Мои кейсы'))
    builder.add(KeyboardButton(text='💱 Одиночные инвестиции'))
    builder.add(KeyboardButton(text='💲  Валютные'))
    builder.add(KeyboardButton(text='⭕️ Вернуться в главное меню'))
    builder.adjust(2)
    await message.answer(text=f"Привет {html.bold(html.quote(message.from_user.full_name))}, тут ты можешь посмотреть "
                              "внесенную тобой информацию по\n◦ Кейсам \n◦ Одиночным покупкам \n◦ Валютам, а так же, "
                              "в случае необходимости, изменить её. На что смотрим?",
                         reply_markup=builder.as_markup(resize_keyboard=True),
                         parse_mode=ParseMode.HTML,
                         )
    await state.set_state(Kabinet_State.Kabinet_main)


@router.message(F.text == "🧰 Мои кейсы", Kabinet_State.Kabinet_main)
async def kabinet_my_cases(message: Message, state: FSMContext):
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
    builder2.add(KeyboardButton(text='⭕️ Вернуться в главное меню'))
    builder2.adjust(1)
    text = await database.take_names_and_prices(user_id=message.from_user.id)
    # print(text)
    if text == []:
        builder
        await message.answer(text="Ты еще не добавил кейсов в свой кабинет. Можешь добавить сейчас, нажав на кнопку ниже или сделать это позже на этой странице или на странице отслеживания.",
                             reply_markup=builder2.as_markup(resize_keyboard=True),
                             parse_mode=ParseMode.HTML,
                             )
    else:
        msg = ''
        for lot in text:
            # print("lot ",lot)
            msg = msg + f'\n{lot[3]}.{html.bold(lot[0])} купленный за {html.bold(lot[1])} рублей'
            if lot[2] is not None: msg = msg + f' <i>({lot[2]})</i>'
        await message.answer(text=f"Твои кейсы:{msg}.\nХочешь изменить информацию?",
                             reply_markup=builder.as_markup(resize_keyboard=True),
                             parse_mode=ParseMode.HTML,
                             )
    await state.set_state(Kabinet_State.Kabinet_cases)


@router.message(F.text == '◀️ Назад', Kabinet_State())
async def kabinet_back(message: Message, state: FSMContext):
    print('поймал команду Съебаться')
    await state.clear()
    await kabinet_main_page(message, state)


@router.message(F.text == '➕ Добавить', Kabinet_State.Kabinet_cases)
async def kabinet_new(message: Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='⭕️ Вернуться в главное меню'))
    await message.reply(text='Отправь пожалуйста ссылку на стим маркет нужного тебе кейса и больше ничего не добавляй '
                             'в сообщение.',
                        reply_markup=builder.as_markup(resize_keyboard=True)
                        )
    await state.set_state(Kabinet_State.Kabinet_cases_new_ask)


@router.message(F.text, Kabinet_State.Kabinet_cases_new_ask)
async def kabinet_new_ask(message: Message, state: FSMContext):
    await message.reply(text='За сколько ты его купил?')
    await state.update_data(link=message.text)
    await state.set_state(Kabinet_State.Kabinet_cases_new_ask_price)


@router.message(F.text, Kabinet_State.Kabinet_cases_new_ask_price)
async def kabinet_new_ask_price(message: Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='⭕️ Вернуться в главное меню'))
    await state.update_data(price=message.text)
    await message.reply(text='Принято, ждем добавления...⏳')
    user_data = await state.get_data()
    text = await database.add_case(user_data, user_id=message.from_user.id)
    msg = (f'{text['name']} был добавлен в твою базу данных со стоимостью в {user_data['price']}.'
           '\nХочешь добавить комментарий к этой закупке? '
           'Можешь написать его сообщением или, если нет, то жми на кнопку')
    await message.answer(text=msg,
                         reply_markup=builder.as_markup(resize_keyboard=True)
                         )
    await state.set_state(Kabinet_State.Kabinet_cases_new_ask_komment)


@router.message(F.text, Kabinet_State.Kabinet_cases_new_ask_komment)
async def kabinet_new_ask_komment(message: Message, state: FSMContext):
    await state.update_data(komment=message.text)
    await database.add_komment(user_data=await state.get_data(), user_id=message.from_user.id)
    await message.reply(text='Принято.')
    await state.clear()
    await kabinet_my_cases(message, state)


@router.message(F.text == '❔ Изменить', Kabinet_State.Kabinet_cases)
async def kabinet_new(message: Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='◀️ Назад'))
    builder.add(KeyboardButton(text='⭕️ Вернуться в главное меню'))
    await message.answer(text='Напиши в чат id кейса, информацию о котором ты хочешь изменить.'
                              '\nID пишется в списке перед его названием, при их выводе, в кабинете. '
                              'Через запятую после ID ты должен написать что хочешь изменить из списка '
                              '(<u>название</u>, <u>цена закупки</u>, <u>комментарий</u>)'
                              f'\nПример команды: {html.bold('32, комментарий')}',
                         parse_mode=ParseMode.HTML,
                         reply_markup=builder.as_markup(resize_keyboard=True)
                         )
    await state.set_state(Kabinet_State.Kabinet_cases_chng_ask)


@router.message(F.text, Kabinet_State.Kabinet_cases_chng_ask)
async def kabinet_change_ask(message: Message, state: FSMContext):
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
        await state.set_state(Kabinet_State.Kabinet_cases_chng_ask)
    elif msg[1] not in changes_list:
        print('предложенного параметра нет в списке')
        await message.reply(text='Тебе надо отправить ID и через запяную написать что изменить, как в примере в прошлом сообщении. Используй что-то одно из (<u>название</u>, <u>цена закупки</u>, <u>комментарий</u>)\n<b>ID</b>,<b>что изменить</b>',
                            parse_mode=ParseMode.HTML,
                            reply_markup=builder.as_markup(resize_keyboard=True)
                            )
        await message.answer(text='Давай ты попробуешь еще раз.')
        await state.set_state(Kabinet_State.Kabinet_cases_chng_ask)
    elif not msg[0].isdigit():
        print('id написан не цифрой')
        await message.reply(text='Тебе надо отправить числовой ID, он пишется перед названием кейса.\n<b>ID</b>,<b>что изменить</b>',
                            parse_mode=ParseMode.HTML,
                            reply_markup=builder.as_markup(resize_keyboard=True)
                            )
        await message.answer(text='Давай ты попробуешь еще раз.')
        await state.set_state(Kabinet_State.Kabinet_cases_chng_ask)
    else:
        await state.update_data(change_case_id=msg[0])
        change = await take_change(changes_list.index(msg[1]))
        await state.update_data(change_case_changeitem=change)
        await message.reply(text=f'Хорошо, напиши в следующем сообщении на какое значение ты хочешь поменять параметр {change}',
                            parse_mode=ParseMode.HTML,
                            reply_markup=builder.as_markup(resize_keyboard=True)
                            )
        await state.set_state(Kabinet_State.Kabinet_cases_chng_value)

@router.message(F.text, Kabinet_State.Kabinet_cases_chng_value)
async def kabinet_change_ask_value(message: Message, state: FSMContext):
    await message.reply(text='Хорошо, изменения направлены в базу, сейчас покажу что получилось')
    await state.update_data(change_case_changenew=message.text)
    user_data = await state.get_data()
    result = await database.change_smth(user_data, user_id=message.from_user.id)
    if result is True:
        await state.clear()
        await kabinet_my_cases(message, state)
    else:
        await message.answer(text='Что-то пошло не так при изменении данных в базе...')
        await state.clear()
        await kabinet_main_page(message, state)


async def kabinet_main():
    # Объект бота
    bot = Bot(config.bot_token)
    router = Dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)
    await router.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(kabinet_main())
