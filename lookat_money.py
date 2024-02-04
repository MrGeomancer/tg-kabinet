import asyncio
from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Router, Bot, Dispatcher, html
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton, CallbackQuery, InlineKeyboardButton
import logging

import parsing

router = Router()

@router.message(F.text == "📈 Посмотреть на валюты")
async def kabinet_main_page(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Нажми меня",
        callback_data="random_value"))
    await state.clear()
    data_list = await parsing.get_money_currency(message.from_user.id)
    if data_list == '':
        ttext = 'База данных пустая и смотреть тут не на что 👀‼️. Сначала зайди в кабинет и добавить кейсы.'
        await message.answer(text=ttext, parse_mode=ParseMode.HTML)
    else:
        ttext = ''
        for item in data_list.items():
            ttext+=f'{item[0]}. <b>{item[1]['name']}</b> сейчас можно продать за <b>{item[1]['nowprice']} </b>'
            nowpricedigit = float(item[1]['nowprice'].replace(',','.'))
            if nowpricedigit>item[1]['price']: ttext+=f'🟢 Выгода:<b> x{round(nowpricedigit/item[1]['price'],2)}</b>\n'
            else: ttext+=f'🟥 В минусе:<b> x{round(nowpricedigit/item[1]['price'],2)}</b>\n'
        await message.answer(text=ttext, parse_mode=ParseMode.HTML,
                             reply_markup=builder.as_markup())
    # print(textt)
    # await message.answer(text=textt)


@router.callback_query(F.data == "random_value")
async def send_random_value(callback: CallbackQuery):
    await callback.message.answer(str(randint(1, 10)))
    await callback.answer(
        text="Спасибо, что воспользовались ботом!",
        show_alert=True
    )
