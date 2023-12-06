import sqlite3
con = sqlite3.connect('archives.db')
# con.execute("INSERT INTO URLs(URL) values('金沢駅.jpg')")
# con.commit()

cur = con.execute("SELECT * FROM URLs")
for row in cur:
    print(row)
cur.close()
con.close()