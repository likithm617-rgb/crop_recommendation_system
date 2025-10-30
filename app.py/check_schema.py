import sqlite3

conn = sqlite3.connect('your_database.db')  # Replace with your actual DB file path
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(soil_reports);")
columns = cursor.fetchall()

for col in columns:
    print(col)

conn.close()