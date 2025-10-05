import sqlite3

conn = sqlite3.connect("customers.db")
cur = conn.cursor()

cur.execute("""
SELECT id, name, email, phone, address, preferred_contact, created_at
FROM customers
""")

for row in cur.fetchall():
    print(row)

conn.close()
