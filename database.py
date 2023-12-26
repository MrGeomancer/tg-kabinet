import sqlite3

with sqlite3.connect('database.db') as db:
    cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS cases(
    caseid INTEGER PRIMARY KEY,
    userid TEXT,
    url TEXT,
    token TEXT,
    name TEXT,
    price REAL DEFAULT (0) 
    )""")
    db.commit()

async def take_names_and_prices(user_id):
    # print(user_id)
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT name, price FROM cases WHERE userid = ?", [user_id])
        cases = cursor.fetchall()
        # print(cases)
        db.commit()
        return cases