import sqlite3

connection = sqlite3.connect('library.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Optional: Add initial seed data
cur.execute(
    "INSERT INTO books (title, author, isbn, status, issued_to) VALUES (?, ?, ?, ?, ?)",
    ('The God of Small Things', 'Arundhati Roy', '9780143028574', 'Available', None)
)
cur.execute(
    "INSERT INTO books (title, author, isbn, status, issued_to) VALUES (?, ?, ?, ?, ?)",
    ('Wings of Fire', 'A.P.J. Abdul Kalam', '9788173711466', 'Issued', 'Rohan Sharma')
)

connection.commit()
connection.close()

print("Database initialised successfully.")