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


async def sravnenie(user_data):
    first_g = user_data['gr_1']
    first_p = user_data['pr_1']
    second_g = user_data['gr_2']
    second_p = user_data['pr_2']
    try:
        a = first_p / first_g
        b = second_p / second_g
        if a < b:
            d = a * 0.33
            if (a + d) < b and b / (a + d) > 1.05:
                c = f'{first_p} рублей за {first_g} грамм выгоднее,\nчем {second_p} рублей за {second_g} грамм!\nОчень выгодно!'
                e = '1️⃣ Первый продукт лучше!'
            else:
                c = '%s рублей за %s грамм выгоднее,\nчем %s рублей за %s грамм!' % (
                    first_p, first_g, second_p, second_g)
                e = '1️⃣ Первый продукт лучше!'
        elif a == b:
            c = '⏸У них одинаковая цена'
            e = ""
        else:
            d = b * 0.33
            if (b + d) < a and a / (b + d) > 1.05:
                c = '%s рублей за %s грамм выгоднее,\nчем %s рублей за %s грамм!\nОчень выгодно!' % (
                    second_p, second_g, first_p, first_g)
                e = '2️⃣ Второй продукт лучше!'
            else:
                c = '%s рублей за %s грамм выгоднее,\nчем %s рублей за %s грамм!' % (
                    second_p, second_g, first_p, first_g)
                e = '2️⃣ Второй продукт лучше!'
        return c +'\n'+ e
    except:
        return 'Ошибка'


@router.message(F.text == "🛒 Сравнить цены")
async def sravnenie_cen1(message: Message, state: FSMContext):
    # print('зашел')
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='⭕️ Вернуться в главное меню'))
    await state.clear()
    await message.answer(text="Сколько грамм у первого продукта?", reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(Sravn_State.Sravnenie_gr_1)


@router.message(F.text, Sravn_State.Sravnenie_gr_1)
async def sravnenie_cen2(message: Message, state: FSMContext):
    # print('зашел в состояние введенных граммов')
    msg = message.text
    try:
        msg = float(msg.replace(",", "."))
        if msg < 10:
            await state.update_data(gr_1=msg*1000)
        else:
            await state.update_data(gr_1=msg)
        await message.reply('Принято, сколько он стоит?')
        await state.set_state(Sravn_State.Sravnenie_price_1)
    except:
        await message.reply('Вводи пожалуйста только цифры')
        await state.set_state(Sravn_State.Sravnenie_gr_1)

@router.message(F.text, Sravn_State.Sravnenie_price_1)
async def sravnenie_cen3(message: Message, state: FSMContext):
    # print('зашел в состоние введенной цены')
    msg = message.text
    try:
        msg = float(msg.replace(",", "."))
        await state.update_data(pr_1=msg)
        await message.answer('А сколько грамм у второго продукта?')
        await state.set_state(Sravn_State.Sravnenie_gr_2)
    except:
        await message.reply('Вводи пожалуйста только цифры')
        await state.set_state(Sravn_State.Sravnenie_price_1)


@router.message(F.text, Sravn_State.Sravnenie_gr_2)
async def sravnenie_cen4(message: Message, state: FSMContext):
    # print('зашел в состояние введенных граммов2')
    msg = message.text
    try:
        msg = float(msg.replace(",", "."))
        if msg < 10:
            await state.update_data(gr_2=msg*1000)
        else:
            await state.update_data(gr_2=msg)
        await message.reply('Принято, сколько стоит второй продукт?')
        await state.set_state(Sravn_State.Sravnenie_price_2)
    except:
        await message.reply('Вводи пожалуйста только цифры')
        await state.set_state(Sravn_State.Sravnenie_gr_2)

@router.message(F.text, Sravn_State.Sravnenie_price_2)
async def sravnenie_result(message: Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='✅ Продолжить'))
    builder.add(KeyboardButton(text='⭕️ Вернуться в главное меню'))
    builder.adjust(1)
    # print('зашел в состоние введеннх всех')
    msg = message.text
    try:
        msg = float(msg.replace(",", "."))
        await state.update_data(pr_2=msg)
        user_data = await state.get_data()
        text = await sravnenie(user_data)
        await message.answer(text)
        await state.clear()
        await state.set_state(Sravn_State.Sravnenie_price_result)
        await message.answer(f'Продолжим сравнивать или вернемся в главное меню?',
                             reply_markup=builder.as_markup(resize_keyboard=True)
                             )
    except:
        await message.reply('Вводи пожалуйста только цифры')
        await state.set_state(Sravn_State.Sravnenie_price_2)


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
