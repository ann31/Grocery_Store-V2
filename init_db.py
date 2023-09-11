import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO items (itemName, price, categoryid, stock ) VALUES (?, ?, ?, ?)",
            ('Carrot', 7, 1, 15)
            )
cur.execute("INSERT INTO category (categoryName, ran) VALUES (?,?)",
            ('veggies', 0)
            )
cur.execute("INSERT INTO user (userName, email, userPassword, adminRights) VALUES (?,?,?,?)",
            ('admin','admin@abc.com', 'abc', 1))
connection.commit()
connection.close()