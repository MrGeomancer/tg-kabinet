import sqlite3
import logging

import parsing

with sqlite3.connect('database.db') as db:
    cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS cases(
    caseid INTEGER PRIMARY KEY,
    userid TEXT,
    url TEXT,
    token TEXT,
    name TEXT,
    price REAL DEFAULT (0),
    count INTEGER DEFAULT (1),
    komment TEXT,
    lastprice REAL DEFAULT (0),
    timecheck TEXT DEFAULT (0)
    )""")
    db.commit()


async def take_names_and_prices(user_id):
    # print(user_id)
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT name, price, komment, caseid, count FROM cases WHERE userid = ?", [user_id])
        cases = cursor.fetchall()
        # print(cases)
        db.commit()
        return cases


async def add_case(user_data, user_id):
    #
    #добавить сюда проверку дублей, если кейс уже есть в базе, то не парсить его
    #
    #
    name_token = await parsing.get_name_token(user_data['link'])
    print(user_data)
    print('name_token:' ,name_token)
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO cases (userid, url, token, name, price, count) VALUES (?, ?, ?, ?, ?, ?)",
                           (user_id, user_data['link'],name_token['token'], name_token['name'], user_data['price'], user_data['count']))
            db.commit()
            return name_token
        except Exception as e:
            print('Ошибка при добавлении в таблицу\n', e)
            db.commit()


async def add_komment(user_data, user_id):
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute('SELECT caseid FROM cases WHERE userid = ?', [user_id])
        caseids = cursor.fetchall()
        # print(caseids)
        cursor.execute('UPDATE cases SET komment = ? WHERE userid = ? AND url = ? AND caseid = ?',
                       [user_data['komment'], user_id, user_data['link'], caseids[-1][0]])
        db.commit()

async def change_smth(user_data, user_id):
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        try:
            if user_data['change_case_changeitem'] == 'name':
                cursor.execute('UPDATE cases SET name = ? WHERE userid =? AND caseid = ?',[
                                user_data['change_case_changenew'], user_id, user_data['change_case_id']
                               ])
            elif user_data['change_case_changeitem'] == 'price':
                cursor.execute('UPDATE cases SET price = ? WHERE userid =? AND caseid = ?',[
                                user_data['change_case_changenew'], user_id, user_data['change_case_id']
                               ])
            elif user_data['change_case_changeitem'] == 'description':
                cursor.execute('UPDATE cases SET komment = ? WHERE userid =? AND caseid = ?',[
                                user_data['change_case_changenew'], user_id, user_data['change_case_id']
                               ])
            elif user_data['change_case_changeitem'] == 'count':
                cursor.execute('UPDATE cases SET count = ? WHERE userid =? AND caseid = ?',[
                                user_data['change_case_changenew'], user_id, user_data['change_case_id']
                               ])
            db.commit()
            return True
        except Exception as e:
            print('Ошибка при измененнии чего-то в таблице\n', e)
            db.commit()


async def del_case(user_data, user_id):
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        try:
            for item in user_data:
                cursor.execute('DELETE FROM cases WHERE caseid =?',[item])
            db.commit()
            return f'Кейсы с ID {user_data} удалены'
        except Exception as e:
            logging.error('Error at %s', 'def del_case', exc_info=e)
            return f'Ошибка\n{e}\nПередай её комунибудь, умоляю!!!'


async def get_tokens(user_id):
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT token, name, price, count, lastprice, timecheck FROM cases WHERE userid = ?", [user_id])
        for_parsing = cursor.fetchall()
        # print(cases)
        db.commit()
        dict_for_parsing = {}
        i=0
        # print(for_parsing)
        for item in for_parsing:
            # print(item)
            dict_for_parsing.update({i:{'name':item[1],'token':item[0],'price':item[2],'count':item[3],'lastprice':item[4], 'timecheck':item[5]}})
            i += 1
        return dict_for_parsing
