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
    text = await database.take_names_and_prices(user_id=message.from_user.id)
    msg = ''
    for lot in text:
        msg = msg + f'\n◦{html.bold(lot[0])} купленный за {html.bold(lot[1])} рублей'
    await message.answer(text=f"Твои кейсы:{msg}.\nХочешь изменить информацию?",
                         reply_markup=builder.as_markup(resize_keyboard=True),
                         parse_mode=ParseMode.HTML,
                         )
    await state.set_state(Kabinet_State.Kabinet_cases)


@router.message(F.text == '◀️ Назад', Kabinet_State.Kabinet_cases)
async def kabinet_back(message: Message, state: FSMContext):
    await state.clear()
    await kabinet_main_page(message,state)


@router.message(F.text == '➕ Добавить', Kabinet_State.Kabinet_cases)
async def kabinet_new(message: Message, state: FSMContext):
    await message.reply(text='Отправь пожалуйста ссылку на стим маркет нужного тебе кейса и больше ничего не добавляй в сообщение.')
    await state.set_state(Kabinet_State.Kabinet_cases)




async def kabinet_main():
    # Объект бота
    bot = Bot(config.bot_token)
    router = Dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)
    await router.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(kabinet_main())