# Seein entries

import sqlite3

conn = sqlite3.connect("rrp.db")
c = conn.cursor()

# Fetch all records
c.execute("SELECT * FROM professor WHERE pid=101")
print(c.fetchall())
rows = c.fetchall()
if not c.fetchone():
    print("HOOOO")

# Print results
for row in rows:
    print(row)

conn.close()