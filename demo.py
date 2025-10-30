import sqlite3

conn = sqlite3.connect('your_database.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(soil_reports);")
columns = cursor.fetchall()

for col in columns:
    print(col[1])  # prints column names

conn.close()