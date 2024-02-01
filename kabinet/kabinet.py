import asyncio
from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Router, Bot, Dispatcher, html
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton

import config
from kabinet import cases, byones, money

router = Router()
router.include_routers(cases.router, money.router)


@router.message(F.text == "👨‍🏫 Мой кабинет")
async def kabinet_main_page(message: Message, state: FSMContext):
    # print('зашел в кабинет')
    await state.clear()
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='🧰 Мои кейсы'))
    # builder.add(KeyboardButton(text='💱 Одиночные инвестиции'))
    builder.add(KeyboardButton(text='💲  Валютные'))
    builder.add(KeyboardButton(text='⭕️ Вернуться в главное меню'))
    builder.adjust(2)
    await message.answer(text=f"Привет {html.bold(html.quote(message.from_user.full_name))}, тут ты можешь посмотреть "
                              "внесенную тобой информацию по\n◦ Кейсам \n"
                              # "◦ Одиночным покупкам \n"
                              "◦ Валютам,\nа так же, "
                              "в случае необходимости, изменить её. На что смотрим?",
                         reply_markup=builder.as_markup(resize_keyboard=True),
                         parse_mode=ParseMode.HTML,
                         )

@router.message(F.text == '◀️ Назад', cases.Kabinet_сases_state.Kabinet_cases)
@router.message(F.text == '◀️ Назад', money.Kabinet_money_state.Kabinet_money)
async def kabinet_back(message: Message, state: FSMContext):
    # print('поймал команду Съебаться')
    await state.clear()
    await kabinet_main_page(message, state)


async def kabinet_main():
    # Объект бота
    bot = Bot(config.bot_token)
    router = Dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)
    await router.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(kabinet_main())
