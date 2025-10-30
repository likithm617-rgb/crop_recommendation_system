import sqlite3

conn = sqlite3.connect('your_database.db')  # Replace with your actual DB file name
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in your database:")
for table in tables:
    print(table[0])

conn.close()