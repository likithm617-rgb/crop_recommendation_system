import sqlite3

conn = sqlite3.connect('your_database.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS soil_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_name TEXT,
        location TEXT,
        crop_type TEXT,
        nitrogen REAL,
        phosphorus REAL,
        potash REAL,
        ph_value REAL,
        moisture REAL
    )
''')

conn.commit()
conn.close()

print("soil_reports table created successfully.")