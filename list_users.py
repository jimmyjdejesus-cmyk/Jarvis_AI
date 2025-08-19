import sqlite3

conn = sqlite3.connect('janus_database.db')
cursor = conn.cursor()

cursor.execute('SELECT username, name, role, is_active FROM users')
rows = cursor.fetchall()

print('Users in database:')
for row in rows:
    print(f"Username: {row[0]}, Name: {row[1]}, Role: {row[2]}, Active: {row[3]}")

conn.close()
