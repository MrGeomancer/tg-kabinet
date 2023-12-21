import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State

from aiogram.fsm.context import FSMContext
import config

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(config.bot_token)
dp = Dispatcher()

class Sravn_State(StatesGroup):
    Sravnenie_gr_1 = State()
    Sravnenie_price_1 = State()
    Sravnenie_gr_2 = State()
    Sravnenie_price_2 = State()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def reply_builder(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='📈 Посмотреть на кейсы'))
    builder.add(types.KeyboardButton(text='📈 Посмотреть на валюты'))
    builder.add(types.KeyboardButton(text='🛒 Сравнить цены'))
    builder.add(types.KeyboardButton(text='👨‍🏫 Мой кабинет'))

    builder.adjust(2)
    await message.answer(
        "Привет, добро пожаловать в твой кабинет.\nКакими функциями ты хочешь воспользоваться?",
        reply_markup=builder.as_markup(
            resize_keyboard=True,
            input_field_placeholder="Для навигации пользуйся кнопками с заготовленным текстом"
        )
    )
        
# @dp.message(Text("Сравнить цены"))
# async def

# @dp.message(Command("dice"))
# async def cmd_dice(message: types.Message):
#     await message.answer_dice("🎲")
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())