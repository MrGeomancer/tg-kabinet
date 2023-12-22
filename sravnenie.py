import asyncio
from aiogram.fsm.state import StatesGroup, State
from aiogram import F, Router, Bot, Dispatcher
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton

import config

router = Router()

class Sravn_State(StatesGroup):
    Sravnenie_gr_1 = State()
    Sravnenie_price_1 = State()
    Sravnenie_gr_2 = State()
    Sravnenie_price_2 = State()
    Sravnenie_price_result = State()


@router.message(F.text == "🛒 Сравнить цены")
async def sravnenie_cen1(message: Message, state: FSMContext):
    print('зашел')
    await state.clear()
    await message.answer(text="Сколько грамм у первого продукта?", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Sravn_State.Sravnenie_gr_1)


@router.message(F.text, Sravn_State.Sravnenie_gr_1)
async def sravnenie_cen2(message: Message, state: FSMContext):
    print('зашел в состояние введенных граммов')
    # добавить проверка на всё что угодно кроме текста
    # добавить проверка на числа
    await state.update_data(gr_1=message.text)
    await message.reply('Принято, сколько он стоит?')
    await state.set_state(Sravn_State.Sravnenie_price_1)


@router.message(F.text, Sravn_State.Sravnenie_price_1)
async def sravnenie_cen3(message: Message, state: FSMContext):
    print('зашел в состоние введенной цены')
    # добавить проверка на всё что угодно кроме текста
    # добавить проверка на числа
    await state.update_data(pr_1=message.text)
    await message.answer('А сколько грамм у второго продукта?')
    await state.set_state(Sravn_State.Sravnenie_gr_2)


@router.message(F.text, Sravn_State.Sravnenie_gr_2)
async def sravnenie_cen4(message: Message, state: FSMContext):
    print('зашел в состояние введенных граммов2')
    # добавить проверка на всё что угодно кроме текста
    # добавить проверка на числа
    await state.update_data(gr_2=message.text)
    await message.reply('Принято, сколько стоит второй продукт?')
    await state.set_state(Sravn_State.Sravnenie_price_2)


@router.message(F.text, Sravn_State.Sravnenie_price_2)
async def sravnenie_result(message: Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='✅ Продолжить'))
    builder.add(KeyboardButton(text='⭕️ Вернуться в главное меню'))
    builder.adjust(1)
    print('зашел в состоние введеннх всех')
    # добавить проверка на всё что угодно кроме текста
    # добавить проверка на числа
    await state.update_data(pr_2=message.text)
    user_data = await state.get_data()
    await message.answer(f'{user_data}')
    await state.clear()
    await state.set_state(Sravn_State.Sravnenie_price_result)
    await message.answer(f'Продолжим сравнивать или вернемся в главное меню?',
                         reply_markup=builder.as_markup(resize_keyboard=True)
                         )
@router.message(F.text == '✅ Продолжить', Sravn_State.Sravnenie_price_result)
async def newone_srav(message: Message, state: FSMContext):
    await sravnenie_cen1(message, state)



async def srav_main():
    # Объект бота
    bot = Bot(config.bot_token)
    router = Dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)
    await router.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(srav_main())