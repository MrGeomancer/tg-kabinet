import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F, html, Router
from aiogram.filters import Command, StateFilter
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

import config
import sravnenie
import kabinet

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
last = Router()
bot = Bot(config.bot_token)
dp = Dispatcher()
dp.include_router(sravnenie.router)
dp.include_router(kabinet.router)
# dp.include_router()
dp.include_router(last)


# Хэндлер на команду /start
@dp.message(Command("start"))
async def starting_msg(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='📈 Посмотреть на кейсы'))
    builder.add(types.KeyboardButton(text='📈 Посмотреть на валюты'))
    builder.add(types.KeyboardButton(text='🛒 Сравнить цены'))
    builder.add(types.KeyboardButton(text='👨‍🏫 Мой кабинет'))
    builder.adjust(2)
    if message.text == '/start':
        await message.answer(
            "Привет, добро пожаловать в твой кабинет.\nКакими функциями ты хочешь воспользоваться?",
            reply_markup=builder.as_markup(
                resize_keyboard=True,
                input_field_placeholder="Для навигации пользуйся кнопками с заготовленным текстом"
            )
        )
    else:
        await message.answer(
            'Добро пожаловать домой💪👀👍',
            reply_markup=builder.as_markup(
                resize_keyboard=True,
                input_field_placeholder="Для навигации пользуйся кнопками с заготовленным текстом"
            )
        )


@dp.message(Command("help"))
async def helping_msg(message: types.Message):
    await message.answer(
        f'Привет {html.bold(html.quote(message.from_user.full_name))}, этот бот представляет из себя "кабинет", '
        f'в котором ты можешь отслеживать стоимость своих покупок в стиме, валютного кошелька, их изменения и выгодно '
        f'купить гречки.\nНачать работать с ним можно по команде /start.', parse_mode=ParseMode.HTML,
        reply_markup=types.ReplyKeyboardRemove())


@dp.message(StateFilter(None), Command(commands=["cancel"]))
@dp.message(default_state, F.text.lower() == "отмена")
async def cmd_cancel_no_state(message: types.Message, state: FSMContext):
    # Стейт сбрасывать не нужно, удалим только данные
    await state.set_data({})
    await message.answer(
        text="Нечего отменять",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await starting_msg(message)


@dp.message(Command(commands=["cancel"]))
@dp.message(F.text.lower() == "отмена")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await starting_msg(message)


@dp.message(F.text == "⭕️ Вернуться в главное меню")
async def back_to_main(message: types.Message, state: FSMContext):
    await state.clear()
    await starting_msg(message)


@last.message()
async def nothing(message: types.Message):
    await message.reply('На такую команду я не запрограммирован.')
    await starting_msg(message)


# @dp.message(Command("dice"))
# async def cmd_dice(message: types.Message):
#     await message.answer_dice("🎲")
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
