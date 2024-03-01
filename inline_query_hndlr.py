from aiogram import F, Router, html
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
import logging
import hashlib

router = Router()


@router.inline_query()
async def inline_query(inline_query: InlineQuery, state: FSMContext):
    # print('\n--\n--\ninline_query:',inline_query)
    user_data = await state.get_data()
    # print('\n+\n+\nstate:', user_data)
    ttext = f'тут чтото блять написано и {inline_query.query}'
    # print('text:', ttext)
    input_contend = InputTextMessageContent(message_text=ttext)
    items = []
    if 'datalist_case' in user_data:
        for item in user_data['datalist_case'].items():
            idtext = f'case_{item[0]}'
            result_id = hashlib.md5(idtext.encode()).hexdigest()
            input_contend = InputTextMessageContent(message_text=f"Я в свое время купил {item[1]['count']} шт. {item[1]['name']} на {item[1]['count']*item[1]['price']} рублей. С этой закупки я заработал {(item[1]['count'] * item[1]['price'] * ((float(item[1]['nowprice'][:-5].replace(',', '.'))) / item[1]['price']))-item[1]['count']*item[1]['price']} рублей!")
            items.append(InlineQueryResultArticle(
                input_message_content=input_contend,
                id=result_id,
                title=f"ID{item[0]}: {item[1]['name']}",
                # description='Похвастаться своей прибылью с этой закупки'
                cach_time=5
            ))
    else:
        idtext = f'{inline_query.from_user.id}no money'
        result_id = hashlib.md5(idtext.encode()).hexdigest()
        input_contend= InputTextMessageContent(message_text='Я пользуюсь @tgkabinet_bot для отслеживания своих покупок в стиме и валют и вам советую!')
        items.append(InlineQueryResultArticle(
            input_message_content=input_contend,
            id=result_id,
            title='@tgkabinet_bot',
            description='Ты еще не проверял актуальную цену своих кейсов',
            cach_time=1
        ))

    if 'datalist_money' in user_data:
        for item in user_data['datalist_money'].items():
            idtext = f'case_{item[0]}'
            result_id = hashlib.md5(idtext.encode()).hexdigest()
            input_contend = InputTextMessageContent(message_text=f"Я в свое время купил {item[1]['count']}{item[1]['name']} на {item[1]['count']*item[1]['price']} рублей. С этой закупки я заработал {(item[1]['count'] * item[1]['price'] * ((float(item[1]['nowprice'].replace(',', '.'))) / item[1]['price']))-item[1]['count']*item[1]['price']} рублей!")
            items.append(InlineQueryResultArticle(
                input_message_content=input_contend,
                id=result_id,
                title=f"ID{item[0]}: {item[1]['count']}{item[1]['name']}",
                # description='Похвастаться своей прибылью с этой закупки'
                cach_time=5
            ))
    else:
        idtext = f'{inline_query.from_user.id}no case'
        result_id = hashlib.md5(idtext.encode()).hexdigest()
        input_contend= InputTextMessageContent(message_text='Я пользуюсь @tgkabinet_bot для отслеживания своих покупок в стиме и валют и вам советую!')
        items.append(InlineQueryResultArticle(
            input_message_content=input_contend,
            id=result_id,
            title='@tgkabinet_bot',
            description='Ты еще не проверял актуальную цену своих валют',
            cach_time=1
        ))

    # print(items)
    await inline_query.answer(results=items, is_personal=True)