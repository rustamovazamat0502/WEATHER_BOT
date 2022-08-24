import sqlite3

conn = sqlite3.connect('weather.db')
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS history(
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id BIGINT,
    fullname TEXT,
    city_name TEXT,
    status TEXT,
    wind INTEGER,
    temperature INTEGER
    
)""")

conn.commit()
conn.close()
