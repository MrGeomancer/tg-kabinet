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
    # cursor.execute('SELECT price FROM cases WHERE url = ?', ['qq'])
    # caseid = cursor.fetchone()[0]
    # cursor.execute('ALTER TABLE cases ADD COLUMN userid "TEXT"')