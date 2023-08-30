import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import config

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(config.bot_token)
# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def reply_builder(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Мой кабинет'))
    builder.add(types.KeyboardButton(text='Мои кейсы'))
    builder.add(types.KeyboardButton(text='Посмотреть на валюты'))
    builder.add(types.KeyboardButton(text='Посмотреть на кейсы'))
    builder.adjust(2)
    await message.answer(
        "Какие котлетки?:",
        reply_markup=builder.as_markup(resize_keyboard=True),)

# @dp.message(Command("dice"))
# async def cmd_dice(message: types.Message):
#     await message.answer_dice("🎲")
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())