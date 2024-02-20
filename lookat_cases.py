import asyncio
from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Router, Bot, Dispatcher, html
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton, CallbackQuery, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
import logging

import parsing

router = Router()


class StringToCallbackWithID_case(CallbackData, prefix="fID"):
    action: str
    value: int


class ChangeStranic_case(CallbackData, prefix="stran"):
    action: str
    cur_stranic: int


@router.message(F.text == "📈 Посмотреть на кейсы")
async def kabinet_main_page(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    try:
        data_list = await parsing.get_prices(message.from_user.id)
    except IndexError as e:
        logging.error('словил хуйню %s def kabinet_main_page', exc_info=True)
        data_list = 'IndexError'
    except Exception as e:
        logging.error('словил хуйню %s def kabinet_main_page', exc_info=True)
        await message.answer(text=f'Ошибка, {e}', parse_mode=ParseMode.HTML)
    if data_list == '':
        ttext = 'База данных пустая и смотреть тут не на что 👀‼️. Сначала зайди в кабинет и добавить кейсы.'
        await message.answer(text=ttext, parse_mode=ParseMode.HTML)
    elif data_list == 'IndexError':
        await message.answer(text='Ошибка парсинга сайта стима с ценами')
    else:
        # print(data_list)
        ttext = ''

        i = 0
        ids_case_list = []
        stranica = 1
        await state.update_data(colvo_str_case=(len(data_list) // 5) + 1)
        await state.update_data(elm_on_last_case=len(data_list) % 5)
        await state.update_data(datalist_case=data_list)
        if len(data_list) % 5 == 0:
            await state.update_data(elm_on_last_case=5)

        for item in data_list.items():

            if i < 5:
                builder.button(text=f"ID{item[0]}",
                               callback_data=StringToCallbackWithID_case(action='send_more_info', value=int(f'{item[0]}')))
                i += 1
            ids_case_list.append(f'{item[0]}')

            ttext += f'{item[0]}.<b>{item[1]['name']}</b> сейчас можно продать за <b>{item[1]['nowprice']} </b>'
            nowpricedigit = float(item[1]['nowprice'][:-5].replace(',', '.'))
            if nowpricedigit-(nowpricedigit*0.15) > float(item[1]['price']):
                ttext += f'🟢 Выгода:<b> x{round((nowpricedigit-(nowpricedigit*0.15)) / item[1]['price'], 2)}</b>\n'
            else:
                ttext += f'🟥 В минусе:<b> x{round((nowpricedigit-(nowpricedigit*0.15)) / item[1]['price'], 2)}</b>\n'

        await state.update_data(ids_case=ids_case_list)
        user_data = await state.get_data()
        # print(user_data)
        if user_data['colvo_str_case'] > 1 and user_data['colvo_str_case'] != 2:

            builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))
            builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))
            builder.button(text=f">", callback_data=ChangeStranic_case(action='next_inlbtn_case', cur_stranic=stranica))
            builder.button(text=f">>", callback_data=ChangeStranic_case(action="last_inlbtn_case", cur_stranic=stranica))
        elif user_data['colvo_str_case'] == 2:
            builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))
            builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))
            builder.button(text=f">", callback_data=ChangeStranic_case(action='next_inlbtn_case', cur_stranic=stranica))
            builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))
        builder.adjust(5)
        await message.answer(text=ttext, parse_mode=ParseMode.HTML,
                             reply_markup=builder.as_markup())

    # print(textt)
    # await message.answer(text=textt)


@router.callback_query(StringToCallbackWithID_case.filter(F.action == "send_more_info"))
async def send_more_info(callback: CallbackQuery, callback_data: StringToCallbackWithID_case, state: FSMContext):
    # print (callback_data)
    user_data = await state.get_data()
    data_list = user_data['datalist_case'][callback_data.value]
    data_list.update({'nowpricedigit': float(data_list['nowprice'][:-5].replace(',', '.'))})
    # print(data_list)
    ttext = f"""Лот №{callback_data.value}: <b>{data_list['name']}</b>
Ты купил <b>{data_list['count']} шт.</b> по <b>{data_list['price']}</b> руб. за каждый, а сейчас он вырос в <b>{round(data_list['nowpricedigit'] / data_list['price'], 2)}</b> раз!
То есть, если ты сейчас продашь все свои кейсы по цене <b>{data_list['nowprice']}</b> за каждый, то выйдешь в плюс на <b>{(data_list['count'] * data_list['price'] * (data_list['nowpricedigit'] / data_list['price']))-data_list['count']*data_list['price']} рублей!</b>

<i>Последнее время проверки стоимости: {data_list['timecheck']}
Потрачено на закупку лота: {data_list['count']*data_list['price']} рублей</i>"""
    if data_list['description'] is not None: ttext += f'\n<i>Комментарий закупки: {data_list['description']}</i>'
    await callback.message.answer(ttext, parse_mode=ParseMode.HTML)

    # for item in user_data['datalist_case'][callback_data.value]:
    #     await callback.message.answer(f'Лот №{callback_data.value}:{item}\n'
    #                                   f'{item}, {user_data['datalist_case'][callback_data.value][item]}')
    await callback.answer(
        text="Спасибо, что воспользовались ботом!",
        show_alert=False
    )


@router.callback_query(ChangeStranic_case.filter(F.action == "next_inlbtn_case"))
async def next_inlbtn_case(callback: CallbackQuery, callback_data: ChangeStranic_case, state: FSMContext):
    builder = InlineKeyboardBuilder()
    stranica = callback_data.cur_stranic + 1
    user_data = await state.get_data()
    # await callback.message.answer(text=f'{user_data}')
    i = 0
    for item in user_data['ids_case'][(stranica - 1) * 5:stranica * 5]:
        builder.button(text=f"ID{item}",
                       callback_data=StringToCallbackWithID_case(action='send_more_info', value=int(f'{item}')))
        i += 1
    if i < 5:
        for i in range(5 - i):
            builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))

    if stranica == user_data['colvo_str_case'] and stranica == 2:
        builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))
        builder.button(text=f"<", callback_data=ChangeStranic_case(action="prev_inlbtn_case", cur_stranic=stranica))
        builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))
        builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))
    elif stranica == user_data['colvo_str_case']:
        builder.button(text=f"<<", callback_data=ChangeStranic_case(action="first_inlbtn_case", cur_stranic=stranica))
        builder.button(text=f"<", callback_data=ChangeStranic_case(action="prev_inlbtn_case", cur_stranic=stranica))
        builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))
        builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))
    elif stranica == user_data['colvo_str_case'] - 1 and stranica == 2:
        builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))
        builder.button(text=f"<", callback_data=ChangeStranic_case(action="prev_inlbtn_case", cur_stranic=stranica))
        builder.button(text=f">", callback_data=ChangeStranic_case(action='next_inlbtn_case', cur_stranic=stranica))
        builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))
    else:
        builder.button(text=f"<<", callback_data=ChangeStranic_case(action="first_inlbtn_case", cur_stranic=stranica))
        builder.button(text=f"<", callback_data=ChangeStranic_case(action="prev_inlbtn_case", cur_stranic=stranica))
        builder.button(text=f">", callback_data=ChangeStranic_case(action='next_inlbtn_case', cur_stranic=stranica))
        builder.button(text=f">>", callback_data=ChangeStranic_case(action="last_inlbtn_case", cur_stranic=stranica))

    builder.adjust(5)
    # await callback.message.answer(f'нажата кнопка следующая станица')
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(ChangeStranic_case.filter(F.action == "prev_inlbtn_case"))
async def prev_inlbtn_case(callback: CallbackQuery, callback_data: ChangeStranic_case, state: FSMContext):
    builder = InlineKeyboardBuilder()
    stranica = callback_data.cur_stranic - 1
    user_data = await state.get_data()
    # await callback.message.answer(text=f'{user_data}')
    i = 0
    for item in user_data['ids_case'][(stranica - 1) * 5:stranica * 5]:
        builder.button(text=f"ID{item}",
                       callback_data=StringToCallbackWithID_case(action='send_more_info', value=int(f'{item}')))
        i += 1

    if stranica == 1 and user_data['colvo_str_case'] > 2:
        builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))
        builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))
        builder.button(text=f">", callback_data=ChangeStranic_case(action='next_inlbtn_case', cur_stranic=stranica))
        builder.button(text=f">>", callback_data=ChangeStranic_case(action="last_inlbtn_case", cur_stranic=stranica))
    elif stranica == user_data['colvo_str_case'] - 1 and stranica == 2:
        builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))
        builder.button(text=f"<", callback_data=ChangeStranic_case(action="prev_inlbtn_case", cur_stranic=stranica))
        builder.button(text=f">", callback_data=ChangeStranic_case(action='next_inlbtn_case', cur_stranic=stranica))
        builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))
    elif stranica == 2:
        builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))
        builder.button(text=f"<", callback_data=ChangeStranic_case(action="prev_inlbtn_case", cur_stranic=stranica))
        builder.button(text=f">", callback_data=ChangeStranic_case(action='next_inlbtn_case', cur_stranic=stranica))
        builder.button(text=f">>", callback_data=ChangeStranic_case(action="last_inlbtn_case", cur_stranic=stranica))
    else:
        builder.button(text=f"<<", callback_data=ChangeStranic_case(action="first_inlbtn_case", cur_stranic=stranica))
        builder.button(text=f"<", callback_data=ChangeStranic_case(action="prev_inlbtn_case", cur_stranic=stranica))
        builder.button(text=f">", callback_data=ChangeStranic_case(action='next_inlbtn_case', cur_stranic=stranica))
        builder.button(text=f">>", callback_data=ChangeStranic_case(action="last_inlbtn_case", cur_stranic=stranica))

    builder.adjust(5)
    # await callback.message.answer(f'нажата кнопка предыдущая станица'
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(ChangeStranic_case.filter(F.action == "last_inlbtn_case"))
async def last_inlbtn_case(callback: CallbackQuery, callback_data: ChangeStranic_case, state: FSMContext):
    builder = InlineKeyboardBuilder()
    user_data = await state.get_data()
    stranica = user_data['colvo_str_case']
    elm_on_last_case = user_data['elm_on_last_case'] * -1

    i = 0
    for item in user_data['ids_case'][elm_on_last_case:]:
        builder.button(text=f"ID{item}",
                       callback_data=StringToCallbackWithID_case(action='send_more_info', value=int(f'{item}')))
        i += 1
    if i < 5:
        for i in range(5 - i):
            builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))

    builder.button(text=f"<<", callback_data=ChangeStranic_case(action="first_inlbtn_case", cur_stranic=stranica))
    builder.button(text=f"<", callback_data=ChangeStranic_case(action="prev_inlbtn_case", cur_stranic=stranica))
    builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))
    builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))

    builder.adjust(5)
    # await callback.message.answer(f'нажата кнопка последняя станица')
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(ChangeStranic_case.filter(F.action == "first_inlbtn_case"))
async def first_inlbtn_case(callback: CallbackQuery, callback_data: ChangeStranic_case, state: FSMContext):
    builder = InlineKeyboardBuilder()
    user_data = await state.get_data()
    stranica = 1

    i = 0
    for item in user_data['ids_case'][:5]:
        builder.button(text=f"ID{item}",
                       callback_data=StringToCallbackWithID_case(action='send_more_info', value=int(f'{item}')))
        i += 1
    if i < 5:
        for i in range(5 - i):
            builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))

    builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))
    builder.add(InlineKeyboardButton(text=f" ", callback_data="nothing"))
    builder.button(text=f">", callback_data=ChangeStranic_case(action='next_inlbtn_case', cur_stranic=stranica))
    builder.button(text=f">>", callback_data=ChangeStranic_case(action="last_inlbtn_case", cur_stranic=stranica))

    builder.adjust(5)
    # await callback.message.answer(f'нажата кнопка первая станица')
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    await callback.answer()
