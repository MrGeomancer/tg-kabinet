import asyncio
from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Router, Bot, Dispatcher, html
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton

import config

router = Router()

@router.message(F.text == "👨‍🏫 Мой кабинет")
async def sravnenie_cen1(message: Message, state: FSMContext):
    print('зашел в кабинет')
    await state.clear()
    await message.answer(text=f"Привет {html.bold(html.quote(message.from_user.full_name))}, тут ты можешь посмотреть "
                              "внесенную тобой информацию по\n◦ Кейсам \n◦ Одиночным покупкам \n◦ Валютам, а так же, "
                              "в случае необходимости, изменить её. На что смотрим?",
                         reply_markup=ReplyKeyboardRemove(),
                         parse_mode=ParseMode.HTML,
                         )
    # await state.set_state(Sravn_State.Sravnenie_gr_1)

async def kabinet_main():
    # Объект бота
    bot = Bot(config.bot_token)
    router = Dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)
    await router.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(kabinet_main())