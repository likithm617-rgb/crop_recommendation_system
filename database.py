import sqlite3
import re

# Create database and table
conn = sqlite3.connect('soil_reports.db')
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
    ph REAL,
    moisture REAL,
    interpretation TEXT
)
''')
conn.commit()
conn.close()

# Extract values from OCR text
def extract_values(text):
    text = text.replace("DH", "pH")
    values = extract_all_numbers(text)
    if len(values) >= 4:
        nitrogen = values[0]
        phosphorus = values[1]
        potash = values[2]
        ph = values[3]
        moisture = values[4] if len(values) > 4 else 25.0
        return nitrogen, phosphorus, potash, ph, moisture
    else:
        raise ValueError("Insufficient values detected for mapping.")

# Extract all decimal numbers
def extract_all_numbers(text):
    return [float(match.group()) for match in re.finditer(r"\d+\.\d+", text)]

# Save to database
def save_to_db(farmer_name, location, crop_type, nitrogen, phosphorus, potash, ph, moisture):
    conn = sqlite3.connect('soil_reports.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO soil_reports (farmer_name, location, crop_type, nitrogen, phosphorus, potash, ph, moisture, interpretation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (farmer_name, location, crop_type, nitrogen, phosphorus, potash, ph, moisture, 'Auto-mapped from OCR'))
    conn.commit()
    conn.close()