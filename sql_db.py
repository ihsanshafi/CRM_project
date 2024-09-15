import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('crm.db')
cursor = conn.cursor()

# Create a table for customers
cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT
)
''')

conn.commit()
conn.close()
