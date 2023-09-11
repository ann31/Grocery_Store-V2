import sqlite3

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def viewItems():
    conn = get_db_connection()
    res = []
    categories = conn.execute('SELECT * from category ').fetchall()
    
    for category in categories:
        temp = []
        temp.append(str(category['categoryName']))
        temp.append(int(category['id']))
        query = "SELECT * FROM items where categoryid = " + str(category['id'])+ " ORDER BY unitsSold"
        items = conn.execute(query).fetchall()
        templist = []
    
        for item in items:
            tempitem = {}
            tempitem['id'] = str(item['id']) 
            tempitem['name'] = str(item['itemName']) 
            tempitem['price'] = str(item['price'])
            tempitem['stock'] = str(item['stock'])
            tempitem['categoryid'] = str(item['categoryid'])
            templist.append(tempitem)
        temp.append(templist)
        temp.append(len(templist))
        res.append(temp)
    conn.close()
    return res

def addItem(item, id):
    conn = get_db_connection()
    
    id = int(id)
    conn.execute("INSERT INTO items (itemName, price, stock, categoryid ) VALUES (?, ?, ?, ?)",
            (item[0], int(item[1]), int(item[2]), id))
    
    conn.commit()
    conn.close()
    return True

def newCat(name):
    conn = get_db_connection()
    conn.execute("INSERT INTO category (categoryName, ran) VALUES (?, ?)", (name, 0))
    conn.commit()
    conn.close()
    return True

def fetchItem(id):
    conn = get_db_connection()
    query = "SELECT * FROM items where items.id ==" +id
    item = conn.execute(query).fetchone()
    conn.close()
    return item
    
def viewCart(user):
    conn = get_db_connection()
    query = 'SELECT * FROM cart where userid = ' + str(user)
    items = conn.execute(query).fetchall()
    conn.close()
    return items

def addToCart(id, qty, user):
    conn = get_db_connection()
    query = "SELECT * FROM items where items.id ==" +id
    item = conn.execute(query).fetchone()
    price = int(item['price'])
    qty = int(qty)
    if int(item['stock']) < qty :
        return False
    else:
        conn.execute("UPDATE items SET stock = ? where id = ?",(int(item['stock'])-qty, id))
    
    total = price * qty
    conn.execute("INSERT INTO cart (itemid, item, price, qty, total , categoryid, userid) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (int(item['id']), str(item['itemName']), int(item['price']), int(qty), total, int(item['categoryid']), int(user)))
    conn.commit()
    conn.close()
    return True

def userValidate(email, password):
    conn = get_db_connection()
    temp = []
    users = conn.execute('SELECT * from user').fetchall()
    for user in users:
        if str(user['email']) == email:
            if str(user['userPassword']) == password:
                if user['adminRights'] == 0:
                    temp.append("norm") 
                elif user['adminRights'] == 1:
                    temp.append("admin") 
                elif user['adminRights'] == 2:
                    temp.append("manager")
                temp.append(user['id'])
    if len(temp) == 0:
        temp.append("none")
            
    conn.commit()
    conn.close()
    return temp

def buyItems(user):
    conn = get_db_connection()

    try:
        # Get user's total and shopCount from user table
        query = "SELECT total, shopCount FROM user WHERE id = ?"
        user_data = conn.execute(query, (user,)).fetchone()

        if user_data is None:
            return False  # User not found

        uTotal = user_data['total'] or 0
        uShopCount = user_data['shopCount'] or 0

        # Calculate total based on user's cart items
        cart_total = findTotal(user)

        total = uTotal + cart_total
        count = uShopCount + 1

        # update unitsSold
        items = conn.execute('SELECT * FROM cart where userid = (?)', (user,)).fetchall()
        for item in items:
            id = item['itemid']
            qty = 0
            temp = conn.execute('SELECT * FROM items where id = (?)', (item['itemid'],)).fetchone()
            qty = temp['unitsSold'] + item['qty']
            conn.execute("UPDATE items SET unitsSold = ? WHERE id = ?;", (qty, id))

        # Clear user's cart
        query = "DELETE FROM cart WHERE userid = ?"
        conn.execute(query, (user,))

        # Update user's total and shopCount in the user table
        conn.execute("UPDATE user SET total = ?, shopCount = ? WHERE id = ?;", (total, count, user))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        # Handle exceptions and errors here
        print("An error occurred:", str(e))
        conn.rollback()  # Rollback any changes if an error occurs
        return False


def fetchCartItem(id):
    conn = get_db_connection()
    query = "SELECT * FROM cart where cart.id ==" +id
    item = conn.execute(query).fetchone()
    conn.close()
    return item

def editCart(id,qty, user):
    conn = get_db_connection()

    qty = int(qty)
    if (qty == 0):
        conn.execute('DELETE FROM cart where id = ?', id)
    else:
        item = conn.execute("SELECT * FROM cart WHERE id = ?;", (id,)).fetchone()
        total = int(item['price'])*qty
        conn.execute("UPDATE cart SET qty = ? WHERE id = ?;", (qty, id))
        conn.execute("UPDATE cart SET total = ? WHERE id = ?;", (total, id))

    conn.commit()
    conn.close()
    return True

def editItem(id,qty):
    conn = get_db_connection()

    qty = int(qty)
    if (qty == 0):
        conn.execute('DELETE FROM items where id = ?', id)
    else:
        conn.execute("UPDATE items SET stock = ? WHERE id = ?;", (qty, id))

    conn.commit()
    conn.close()
    return True

def editItemPrice(id,qty):
    conn = get_db_connection()
    qty = int(qty)
    conn.execute("UPDATE items SET price = ? WHERE id = ?;", (qty, id))
    conn.commit()
    conn.close()
    return True

def deleteItem(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM items where id = ?', id)
    conn.commit()
    conn.close()
    return True
    
def createUser(name, email, password, type=0):
    conn = get_db_connection()
    conn.execute("INSERT INTO user (userName, email, UserPassword, adminRights ) VALUES (?, ?, ?, ?)",
            (name, email, password, type))
    print("created", name)

    users = conn.execute("SELECT * FROM user").fetchall()
    for user in users:
        print(user['email'], user['userpassword'])
    conn.commit()
    conn.close()
    return True

def findTotal(user):
    conn = get_db_connection()
    user = str(user)
    query = "SELECT SUM(total) AS total FROM cart WHERE userid = ?"
    result = conn.execute(query, (user,)).fetchone()
    total = result['total'] if result['total'] is not None else 0
    conn.commit()
    conn.close()
    return total

def deleteCart(id):
    conn = get_db_connection()
    
    
    conn.execute('DELETE FROM cart where id = (?)', (id,))

    conn.commit()
    conn.close()
    return True

def fetchCatName(id):
    conn = get_db_connection()

    category = conn.execute('SELECT * FROM category where id = ?', id ).fetchone()

    conn.commit()
    conn.close()
    return str(category['categoryname'])

def searchKey(keyword):
    conn = get_db_connection()
    fin = []
    keyword = "%"+keyword+"%"
    #checking for cetegories
    cat = []
    query = "SELECT * FROM category where categoryName like " +"'"+ keyword + "'"
    categories = conn.execute( query ).fetchall()
    if len(categories) == 0:
        cat.append(False)
    else:  
        cat.append(True)
        res = []
        for category in categories:
            temp = []
            temp.append(str(category['categoryName']))
            temp.append(int(category['id']))
            query = "SELECT * FROM items where categoryid = " + str(category['id'])
            items = conn.execute(query).fetchall()
            templist = []
    
            for item in items:
                tempitem = {}
                tempitem['id'] = str(item['id']) 
                tempitem['name'] = str(item['itemName']) 
                tempitem['price'] = str(item['price'])
                tempitem['stock'] = str(item['stock'])
                tempitem['categoryid'] = str(item['categoryid'])
                templist.append(tempitem)
            temp.append(templist)
            temp.append(len(templist))
            res.append(temp)
        cat.append(res)
    #checking for items
    resItem = []
    res = []
    query = "SELECT * FROM items where itemName like "+"'"+ keyword + "'"
    items = conn.execute( query ).fetchall()
    if len(items) == 0:
        resItem.append(False)
    else:
        resItem.append(True)
        for item in items:
            tempitem = {}
            tempitem['id'] = str(item['id']) 
            tempitem['name'] = str(item['itemName']) 
            tempitem['price'] = str(item['price'])
            tempitem['stock'] = str(item['stock'])
            tempitem['categoryid'] = str(item['categoryid'])
            res.append(tempitem)
        resItem.append(res)

    fin.append(cat)
    fin.append(resItem)    

    conn.commit()
    conn.close()

    return fin 

def createAccReq(name, email, password):
    conn = get_db_connection()
    conn.execute("INSERT INTO requests (reqtype, uName,uEmail, uPass) VALUES (?, ?, ?, ?)",
            ("NewManager",name, email, password))
    conn.commit()
    conn.close()
    return True

def getApp():
    conn = get_db_connection()
    res = []
    app = conn.execute("SELECT * FROM requests ").fetchall()
    if len(app) == 0:
        res.append(False)
    else:
        res.append(True)
        res.append(app)
    conn.commit()
    conn.close()
    return res

def viewReq(id):
    conn = get_db_connection()
    query = "SELECT * FROM requests where id ==" +id
    item = conn.execute(query).fetchone()
    conn.close()
    return item

def delRequest(id):
    conn = get_db_connection()
    query = "DELETE FROM requests where id ==" +str(id)
    conn.execute(query)
    conn.commit()
    conn.close()
    return True

def fetchCat(id):
    conn = get_db_connection()
    query = "SELECT * FROM category where id ==" +id
    item = conn.execute(query).fetchone()
    conn.close()
    return item

def deleteCatReq(id):
    conn = get_db_connection()
    query = "SELECT * FROM category where id ==" +id
    item = conn.execute(query).fetchone()
    conn.execute("INSERT INTO requests (reqtype, catId, catName) VALUES (?, ?, ?)",
            ("DeleteCat", int(id), str(item['categoryName'])))
    conn.commit()
    conn.close()
    return True

def delCategory(id):
    conn = get_db_connection()
    query = "DELETE FROM category where id ==" +str(id)
    conn.execute(query)
    conn.commit()
    print("done cat")
    query = "DELETE FROM items where categoryid ==" +str(id)
    conn.execute(query)
    conn.commit()
    conn.close()
    return True

def fetchusers():
    conn = get_db_connection()
    query = "SELECT * FROM user where adminRights == 0 "
    users = conn.execute(query).fetchall()
    conn.close()
    return users

def itemsInCart(user):
    conn = get_db_connection()
    query = "SELECT * FROM cart where userid = " +str(user)
    cart = conn.execute(query).fetchall()
    conn.close()
    return len(cart)

def userReset(userid):
    conn = get_db_connection()
    conn.execute("UPDATE user SET total = ?, shopCount = ? WHERE id = ?;", (0, 0, userid))

    conn.close()
    return True

def viewReport():
    conn = get_db_connection()
    items = conn.execute("SELECT * FROM items ").fetchall()
    res = []
    temp = ["Item name", "Price","stock remaining", "Units Sold"]
    res.append(temp)
    for item in items:
        temp = []
        temp.append(item['itemName'])
        temp.append(item['price'])
        temp.append(item['stock'])
        temp.append(item['unitsSold'])

        res.append(temp)

    conn.close()
    return res

def fetchMail(id):
    conn = get_db_connection()
    query = "SELECT * FROM user where id ==" +str(id)
    item = conn.execute(query).fetchone()
    conn.close()
    return item['email']
