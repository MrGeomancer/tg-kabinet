import sqlite3

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
    komment TEXT
    )""")
    db.commit()


async def take_names_and_prices(user_id):
    # print(user_id)
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT name, price, komment, caseid FROM cases WHERE userid = ?", [user_id])
        cases = cursor.fetchall()
        # print(cases)
        db.commit()
        return cases


async def add_case(user_data, user_id):
    name_token = await parsing.get_name_token(user_data['link'])
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO cases (userid, url, token, name, price) VALUES (?, ?, ?, ?, ?)",
                           (user_id, user_data['link'],name_token['token'], name_token['name'], user_data['price']))
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
        print(caseids)
        cursor.execute('UPDATE cases SET komment = ? WHERE userid = ? AND url = ? AND caseid = ?',
                       [user_data['komment'], user_id, user_data['link'], caseids[-1][0]])
        db.commit()
