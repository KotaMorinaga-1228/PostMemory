import sqlite3
con = sqlite3.connect("archives.db")
cur = con.cursor()
cur.execute(
    'CREATE TABLE IF NOT EXISTS archives (id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER, URL_id INTEGER, body STRING, secret STRING, date STRING)'
)
cur.execute(
    'CREATE TABLE IF NOT EXISTS URLs (id INTEGER PRIMARY KEY AUTOINCREMENT, URL STRING)'
)

con.commit()

cur.close()
con.close()