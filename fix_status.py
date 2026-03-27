"""
One-time migration: normalize all existing regtb Status values to lowercase.
Run on EC2:  python fix_status.py
"""
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fidoclouddb.sqlite')
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("UPDATE regtb SET Status = LOWER(Status)")
rows = cur.rowcount
conn.commit()

print(f"Normalized {rows} rows.")
cur.execute("SELECT id, UserName, Status FROM regtb")
for r in cur.fetchall():
    print(f"  id={r[0]}  user={r[1]}  status={r[2]}")

conn.close()
print("Done.")
