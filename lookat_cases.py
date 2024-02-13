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


class StringToCallbackWithID(CallbackData, prefix="fID"):
    action: str
    value: int

class ChangeStranic(CallbackData, prefix="stran"):
    action: str
    cur_stranic: int


@router.message(F.text == "📈 Посмотреть на кейсы")
async def kabinet_main_page(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    await state.clear()
    try:
        data_list = await parsing.get_prices(message.from_user.id)
    except Exception as e:
        logging.error('словил хуйню %s def kabinet_main_page', exc_info=True)
        await message.answer(text=f'Ошибка, {e}', parse_mode=ParseMode.HTML)
    if data_list == '':
        ttext = 'База данных пустая и смотреть тут не на что 👀‼️. Сначала зайди в кабинет и добавить кейсы.'
        await message.answer(text=ttext, parse_mode=ParseMode.HTML)
    else:
        # print(data_list)
        ttext = ''

        i = 0
        ids_list = []
        stranica = 1
        await state.update_data(colvo_str=(len(data_list) // 5) + 1)
        await state.update_data(elm_on_last=len(data_list) % 5)
        if len(data_list)%5 == 0:
            await state.update_data(elm_on_last = 5)


        for item in data_list.items():

            if i < 5:
                builder.button(text=f"ID{item[0]}",callback_data=StringToCallbackWithID(action='send_more_info',value=int(f'{item[0]}')))
                i += 1
            ids_list.append(f'{item[0]}')

            ttext+=f'{item[0]}.<b>{item[1]['name']}</b> сейчас можно продать за <b>{item[1]['nowprice']} </b>'
            nowpricedigit = float(item[1]['nowprice'][:-5].replace(',','.'))
            if nowpricedigit>float(item[1]['price']): ttext+=f'🟢 Выгода:<b> x{round(nowpricedigit/item[1]['price'],2)}</b>\n'
            else: ttext+=f'🟥 В минусе:<b> x{round(nowpricedigit/item[1]['price'],2)}</b>\n'

        await state.update_data(ids = ids_list)
        user_data = await state.get_data()
        print(user_data)
        if user_data['colvo_str'] > 1 and user_data['colvo_str'] != 2:


            builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
            builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
            builder.button(text=f">",callback_data=ChangeStranic(action='next_inlbtn', cur_stranic=stranica))
            builder.button(text=f">>",callback_data=ChangeStranic(action="last_inlbtn", cur_stranic=stranica))
        elif user_data['colvo_str'] == 2:
            builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
            builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
            builder.button(text=f">",callback_data=ChangeStranic(action='next_inlbtn', cur_stranic=stranica))
            builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
        builder.adjust(5)
        await message.answer(text=ttext, parse_mode=ParseMode.HTML,
            reply_markup=builder.as_markup())

    # print(textt)
    # await message.answer(text=textt)


@router.callback_query(StringToCallbackWithID.filter(F.action == "send_more_info"))
async def send_more_info(callback: CallbackQuery, callback_data: StringToCallbackWithID, state: FSMContext):
    # print (callback_data)
    await callback.message.answer(f'нажата кнопка с id {callback_data.value}')
    await callback.answer(
        text="Спасибо, что воспользовались ботом!",
        show_alert=False
    )


@router.callback_query(ChangeStranic.filter(F.action =="next_inlbtn"))
async def next_inlbtn(callback: CallbackQuery, callback_data: ChangeStranic, state: FSMContext):
    builder = InlineKeyboardBuilder()
    stranica = callback_data.cur_stranic + 1
    user_data = await state.get_data()
    # await callback.message.answer(text=f'{user_data}')
    i=0
    for item in user_data['ids'][(stranica-1)*5:stranica*5]:
        builder.button(text=f"ID{item}",callback_data=StringToCallbackWithID(action='send_more_info',value=int(f'{item}')))
        i += 1
    if i < 5:
        for i in range (5-i):
            builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))

    if stranica == user_data['colvo_str'] and stranica == 2:
        builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
        builder.button(text=f"<",callback_data=ChangeStranic(action="prev_inlbtn", cur_stranic=stranica))
        builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
        builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
    elif stranica == user_data['colvo_str']:
        builder.button(text=f"<<",callback_data=ChangeStranic(action="first_inlbtn", cur_stranic=stranica))
        builder.button(text=f"<",callback_data=ChangeStranic(action="prev_inlbtn", cur_stranic=stranica))
        builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
        builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
    elif stranica == user_data['colvo_str'] - 1 and stranica == 2:
        builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
        builder.button(text=f"<",callback_data=ChangeStranic(action="prev_inlbtn", cur_stranic=stranica))
        builder.button(text=f">",callback_data=ChangeStranic(action='next_inlbtn', cur_stranic=stranica))
        builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
    else:
        builder.button(text=f"<<",callback_data=ChangeStranic(action="first_inlbtn", cur_stranic=stranica))
        builder.button(text=f"<",callback_data=ChangeStranic(action="prev_inlbtn", cur_stranic=stranica))
        builder.button(text=f">",callback_data=ChangeStranic(action='next_inlbtn', cur_stranic=stranica))
        builder.button(text=f">>",callback_data=ChangeStranic(action="last_inlbtn", cur_stranic=stranica))

    builder.adjust(5)
    await callback.message.answer(f'нажата кнопка следующая станица')
    await callback.answer(

        text="Спасибо, что воспользовались ботом!",
        show_alert=False
    )

    # await callback.message.edit_text(text=callback.message.text, entities=callback.message.entities,reply_markup=builder.as_markup())
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())


@router.callback_query(ChangeStranic.filter(F.action =="prev_inlbtn"))
async def prev_inlbtn(callback: CallbackQuery, callback_data: ChangeStranic, state: FSMContext):
    builder = InlineKeyboardBuilder()
    stranica = callback_data.cur_stranic - 1
    user_data = await state.get_data()
    # await callback.message.answer(text=f'{user_data}')
    i=0
    for item in user_data['ids'][(stranica-1)*5:stranica*5]:
        builder.button(text=f"ID{item}",callback_data=StringToCallbackWithID(action='send_more_info',value=int(f'{item}')))
        i += 1

    if stranica == 1 and user_data['colvo_str'] > 2:
        builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
        builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
        builder.button(text=f">", callback_data=ChangeStranic(action='next_inlbtn', cur_stranic=stranica))
        builder.button(text=f">>", callback_data=ChangeStranic(action="last_inlbtn", cur_stranic=stranica))
    elif stranica == user_data['colvo_str'] - 1 and stranica == 2:
        builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
        builder.button(text=f"<",callback_data=ChangeStranic(action="prev_inlbtn", cur_stranic=stranica))
        builder.button(text=f">",callback_data=ChangeStranic(action='next_inlbtn', cur_stranic=stranica))
        builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
    elif stranica == 2:
        builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
        builder.button(text=f"<",callback_data=ChangeStranic(action="prev_inlbtn", cur_stranic=stranica))
        builder.button(text=f">",callback_data=ChangeStranic(action='next_inlbtn', cur_stranic=stranica))
        builder.button(text=f">>", callback_data=ChangeStranic(action="last_inlbtn", cur_stranic=stranica))
    else:
        builder.button(text=f"<<",callback_data=ChangeStranic(action="first_inlbtn", cur_stranic=stranica))
        builder.button(text=f"<",callback_data=ChangeStranic(action="prev_inlbtn", cur_stranic=stranica))
        builder.button(text=f">",callback_data=ChangeStranic(action='next_inlbtn', cur_stranic=stranica))
        builder.button(text=f">>",callback_data=ChangeStranic(action="last_inlbtn", cur_stranic=stranica))

    builder.adjust(5)
    await callback.message.answer(f'нажата кнопка предыдущая станица')
    await callback.answer(

        text="Спасибо, что воспользовались ботом!",
        show_alert=False
    )

    # await callback.message.edit_text(text=callback.message.text, entities=callback.message.entities,reply_markup=builder.as_markup())
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())


@router.callback_query(ChangeStranic.filter(F.action =="last_inlbtn"))
async def last_inlbtn(callback: CallbackQuery, callback_data: ChangeStranic, state: FSMContext):
    builder = InlineKeyboardBuilder()
    user_data = await state.get_data()
    stranica = user_data['colvo_str']
    elm_on_last = user_data['elm_on_last']*-1

    i=0
    for item in user_data['ids'][elm_on_last:]:
        builder.button(text=f"ID{item}",callback_data=StringToCallbackWithID(action='send_more_info',value=int(f'{item}')))
        i += 1
    if i < 5:
        for i in range (5-i):
            builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))

    builder.button(text=f"<<", callback_data=ChangeStranic(action="first_inlbtn", cur_stranic=stranica))
    builder.button(text=f"<", callback_data=ChangeStranic(action="prev_inlbtn", cur_stranic=stranica))
    builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
    builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))


    builder.adjust(5)
    await callback.message.answer(f'нажата кнопка последняя станица')
    await callback.answer(

        text="Спасибо, что воспользовались ботом!",
        show_alert=False
    )

    # await callback.message.edit_text(text=callback.message.text, entities=callback.message.entities,reply_markup=builder.as_markup())
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())


@router.callback_query(ChangeStranic.filter(F.action =="first_inlbtn"))
async def first_inlbtn(callback: CallbackQuery, callback_data: ChangeStranic, state: FSMContext):
    builder = InlineKeyboardBuilder()
    user_data = await state.get_data()
    stranica = 1

    i=0
    for item in user_data['ids'][:5]:
        builder.button(text=f"ID{item}",callback_data=StringToCallbackWithID(action='send_more_info',value=int(f'{item}')))
        i += 1
    if i < 5:
        for i in range (5-i):
            builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))

    builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
    builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
    builder.button(text=f">", callback_data=ChangeStranic(action='next_inlbtn', cur_stranic=stranica))
    builder.button(text=f">>", callback_data=ChangeStranic(action="last_inlbtn", cur_stranic=stranica))


    builder.adjust(5)
    await callback.message.answer(f'нажата кнопка первая станица')
    await callback.answer(

        text="Спасибо, что воспользовались ботом!",
        show_alert=False
    )

    # await callback.message.edit_text(text=callback.message.text, entities=callback.message.entities,reply_markup=builder.as_markup())
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
