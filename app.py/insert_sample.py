import sqlite3

conn = sqlite3.connect('your_database.db')  # Use your actual DB file name
cursor = conn.cursor()

cursor.execute('''
    INSERT INTO soil_reports (farmer_name, location, crop_type, nitrogen, phosphorus, potash, ph_value, moisture)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', ("Ravi", "Tumakuru", "Ragi", 45.0, 20.0, 30.0, 6.5, 12.0))

conn.commit()
conn.close()

print("Sample data inserted.")