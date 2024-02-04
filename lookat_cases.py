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


@router.message(F.text == "📈 Посмотреть на кейсы")
async def kabinet_main_page(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    await state.clear()
    try: data_list = await parsing.get_prices(message.from_user.id)
    except: await message.answer(text='Ошибка', parse_mode=ParseMode.HTML)
    if data_list == '':
        ttext = 'База данных пустая и смотреть тут не на что 👀‼️. Сначала зайди в кабинет и добавить кейсы.'
        await message.answer(text=ttext, parse_mode=ParseMode.HTML)
    else:
        # print(data_list)
        ttext = ''

        colvo_str = (len(data_list) // 5) + 1
        elm_on_last_str = len(data_list) % 5
        i = 0
        ids_list = []
        stranica = 1

        for item in data_list.items():

            if i < 5:
                builder.button(text=f"ID{item[0]}",callback_data=StringToCallbackWithID(action='send_more_info',value=int(f'{item[0]}')))
                i += 1
            ids_list.append(f'{item[0]}')

            ttext+=f'{item[0]}.<b>{item[1]['name']}</b> сейчас можно продать за <b>{item[1]['nowprice']} </b>'
            nowpricedigit = float(item[1]['nowprice'][:-5].replace(',','.'))
            if nowpricedigit>item[1]['price']: ttext+=f'🟢 Выгода:<b> x{round(nowpricedigit/item[1]['price'],2)}</b>\n'
            else: ttext+=f'🟥 В минусе:<b> x{round(nowpricedigit/item[1]['price'],2)}</b>\n'


        if colvo_str > 1 and not 2:
            builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
            builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
            builder.add(InlineKeyboardButton(text=f">",callback_data="next_inlbtn"))
            builder.add(InlineKeyboardButton(text=f">>",callback_data="last_inlbtn"))
        elif colvo_str == 2:
            builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
            builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
            builder.add(InlineKeyboardButton(text=f">",callback_data="next_inlbtn"))
            builder.add(InlineKeyboardButton(text=f" ",callback_data="nothing"))
        builder.adjust(5)
        await message.answer(text=ttext, parse_mode=ParseMode.HTML,
            reply_markup=builder.as_markup())
    # print(textt)
    # await message.answer(text=textt)


@router.callback_query(StringToCallbackWithID.filter(F.action == "send_more_info"))
async def send_more_info(callback: CallbackQuery, callback_data: StringToCallbackWithID):
    print (callback_data)
    await callback.message.answer(f'нажата кнопка с id {callback_data.value}')
    await callback.answer(
        text="Спасибо, что воспользовались ботом!",
        show_alert=False
    )
