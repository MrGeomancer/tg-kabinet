import requests
from bs4 import BeautifulSoup
import aiohttp
import logging
import re

import database

cookies = {
    'sessionid': '3f508f3dc960c4ec077ddab2',
    'timezoneOffset': '18000,0',
    'Steam_Language': 'russian',
    'browserid': '2895299699782351373',
    'webTradeEligibility': '%7B%22allowed%22%3A1%2C%22allowed_at_time%22%3A0%2C%22steamguard_required_days%22%3A15%2C%22new_device_cooldown_days%22%3A0%2C%22time_checked%22%3A1687720529%7D',
    '_ga': 'GA1.2.1815743433.1687720529',
    'steamCountry': 'RU%7Cf786fce45ccb3e777a33903acb1c1f31',
    'recentlyVisitedAppHubs': '1328660%2C2532550%2C1170970%2C814380%2C1222140%2C761890%2C304930%2C1517290%2C615530%2C239140%2C2073850%2C1272080%2C872200%2C730%2C255710%2C508440%2C931690%2C1117090%2C1174180%2C632470',
    'steamLoginSecure': '76561198165608999%7C%7CeyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MEQwNF8yMkQyOEYxM18zOTQyOCIsICJzdWIiOiAiNzY1NjExOTgxNjU2MDg5OTkiLCAiYXVkIjogWyAid2ViIiBdLCAiZXhwIjogMTcwMzMxODQ1NiwgIm5iZiI6IDE2OTQ1OTE5NzIsICJpYXQiOiAxNzAzMjMxOTcyLCAianRpIjogIjBERDZfMjNBQkNEQ0NfNDQ4NzciLCAib2F0IjogMTY4OTI2MTE5NiwgInJ0X2V4cCI6IDE3MDcyNzQ2MTAsICJwZXIiOiAwLCAiaXBfc3ViamVjdCI6ICIxODguMjI2LjExMC4xMCIsICJpcF9jb25maXJtZXIiOiAiMTg4LjIyNi4xMTAuMTAiIH0.vLxT_tUURURYcIpWyTiKnJKv_WWdGSA7VPLHToJ6cPhflM3BDSumBYpgZWPfnnSX0oT27dWNfTRKa87qDm7_AQ',
    'strInventoryLastContext': '252490_2',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Referer': 'https://steamcommunity.com/market/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}


async def get_html(url):
    global cookies, headers
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, cookies=cookies, headers=headers) as resp:
                return await resp.text()
        except Exception as e:
            logging.error('def parsing.get_html', exc_info=True)

async def get_name_token(url):
    # print(url)
    name_token = {'name':"", 'token':""}
    while name_token['name'] == "":
        response = await get_html(url)
        case_page = BeautifulSoup(response, 'lxml')
        token_div = str(case_page.find("div", 'responsive_page_template_content'))
        token = (token_div[token_div.index('Market_LoadOrderSpread') + 24
                           :
                           token_div.index('PollOnUserActionAfterInterval') - 23])
        name = str(case_page.find('span', 'market_listing_item_name').text)
        # print('имя',name,'токен',token)
        name_token['name'], name_token['token'] = name,token
    return name_token


async def get_prices(user_id):
    data_list = await database.get_tokens(user_id)
    if data_list == {}:
        return ''
        logging.error(f'База данных у пользователя {user_id} пустая')
    # print('data_list:',data_list)
    # print('data_list.values',data_list.values())

    ### новый вариант вариант
    tokens = []
    for item in data_list.values():
        # print(item)
        if item['token'] not in tokens:
            tokens.append(item['token'])
    for token in tokens:
        url = f'https://steamcommunity.com/market/itemordershistogram?country=RU&language=russian&currency=5&item_nameid={token}'
        response = await get_html(url)
        price_page = str(BeautifulSoup(response, 'lxml'))
        price=price_page.split(r"""Начальная цена: <span class='\"market_commodity_orders_header_promote\"'>""")[2].split(r'&lt;\/span&gt;')[0]
        for item in data_list.values():
            if item['token'] == token:
                item.update({'nowprice':price})

    ### старый вариант
    # for item in data_list.values():
    #     # print(item)
    #     token = item['token']
    #     # print('token:',token)
    #     url = f'https://steamcommunity.com/market/itemordershistogram?country=RU&language=russian&currency=5&item_nameid={token}'
    #     response = await get_html(url)
    #     price_page = str(BeautifulSoup(response, 'lxml'))
    #     price=price_page.split(r"""Начальная цена: <span class='\"market_commodity_orders_header_promote\"'>""")[2].split(r'&lt;\/span&gt;')[0]
    #     # print(price_page)
    #     item.update({'nowprice':price})
    #     # print('newitem:',item)
    #     # buy_order_summary
    await database.update_lastprice(data_list, 'cases')
    return data_list

async def get_money_currency(user_id):
    data_list = await database.get_money_data(user_id)
    if data_list == {}:
        return ''
        logging.warning(f'База данных у пользователя {user_id} пустая')
    GOLDinmoney, currencyinmoney = False, False
    for item in data_list.values():
        if item['name'] == 'GOLD':
            GOLDinmoney = True
        elif item['name'] in ['USD', 'EUR', 'CHY', 'AED']:
            currencyinmoney = True
        if GOLDinmoney == True and currencyinmoney == True:
            break
    if GOLDinmoney:
        url = 'https://rub24.com/an/kot-gold-sber.php'
        response = await get_html(url)
        list = str(response)
        gold_list=eval(list)
        gold_data={'GOLD':{'date':gold_list[0]['DATE'],'SELL':gold_list[0]['VAL1'],'BUY':gold_list[1]['VAL1']}}
    if currencyinmoney:
        url = 'https://bankiros.ru/bank/sberbank/currency'
        response = await get_html(url)
        money_page = BeautifulSoup(response, 'lxml')
        currency_div = str(money_page.find_all("span", "cursor-pointer"))
        currency_values = re.findall(r'\d+.\d+', currency_div)
        value_data = {'USD':{'SELL':currency_values[0],'BUY':currency_values[1]},
                      'EUR':{'SELL':currency_values[2],'BUY':currency_values[3]},
                      'CNY':{'SELL':currency_values[4],'BUY':currency_values[5]}
                      }
                      # ,'AED':{'SELL':currency_values[8],'BUY':currency_values[9]}}
    for item in data_list.values():
        if item['name'] == 'GOLD':
            item.update({'nowprice':gold_data['GOLD']['SELL']})
        # elif item['name'] == 'USD':
        #     item.update({'nowprice':value_data['USD']['SELL']})
        # elif item['name'] == 'EUR':
        #     item.update({'nowprice':value_data['EUR']['SELL']})
        # elif item['name'] == 'CHY':
        #     item.update({'nowprice':value_data['CHY']['SELL']})
        # elif item['name'] == 'AED':
        #     item.update({'nowprice':value_data['AED']['SELL']})
        elif item['name'] in ['USD', 'EUR', 'CHY', 'AED']:
            currency = item['name']
            item['nowprice'] = value_data[currency]['SELL']
    # print(data_list)
    await database.update_lastprice(data_list, 'money')
    return data_list


if __name__ == "__main__":
    get_name_token('https://steamcommunity.com/market/listings/730/Snakebite%20Case')
