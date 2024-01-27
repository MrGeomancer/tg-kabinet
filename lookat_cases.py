import asyncio
from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Router, Bot, Dispatcher, html
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton
import logging

import parsing

router = Router()

@router.message(F.text == "📈 Посмотреть на кейсы")
async def kabinet_main_page(message: Message, state: FSMContext):
    await state.clear()
    data_list = await parsing.get_pricec(message.from_user.id)
    ttext = ''
    for item in data_list.values():
        nowpricedigit = float(item['nowprice'][:-5].replace(',','.'))
        if nowpricedigit>item['price']: ttext+='🟢'
        else: ttext+='🟥'
        ttext+=f'<b>{item['name']}</b> сейчас можно продать за <b>{item['nowprice']}</b>\n'
    await message.answer(text=ttext, parse_mode=ParseMode.HTML)
    # print(textt)
    # await message.answer(text=textt)
