import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import config

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(config.bot_token)
# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")

@dp.message(Command("dice"))
async def cmd_dice(message: types.Message):
    await message.answer_dice("🎲")
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())