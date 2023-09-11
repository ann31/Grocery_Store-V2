from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm, newCategoryForm, newItemForm, addItemForm, buyForm, editCartForm, editForm, editPriceForm, searchForm
from forms import approveForm, confirmForm, GenerateReportForm
from dbfunc import viewItems, addItem, fetchItem, viewCart, addToCart, userValidate, buyItems, fetchCartItem, editCart, newCat, editItem, deleteItem
from dbfunc import createUser, findTotal, deleteCart, fetchCatName, editItemPrice, searchKey, createAccReq, getApp, viewReq, delRequest, fetchCat
from dbfunc import deleteCatReq, delCategory, fetchusers, itemsInCart, userReset, fetchMail
from flask import request, Response
from reportGeneration import generateReport
import redis
import asyncio
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from dbfunc import viewReport
import io
import csv
from flask import Response

app = Flask(__name__)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'grocerystore031@gmail.com'
app.config['MAIL_PASSWORD'] = 'latkokjxmmfhmhqo'
app.config['MAIL_USE_TLS'] = True

mail = Mail(app)

redis_client = redis.Redis(host='localhost', port=6379, db=0)

global userid 
# protect against modyfying cooking, cross site request forgery attacks etc
app.config['SECRET_KEY'] = '163e34c5745bafbebe6e4c88794ab33f'

#******************************************************************
#                          Common Pages
#******************************************************************
#welcome page
@app.route("/", methods=['GET','POST'])
def Welcome():

    return render_template("welcome.html")


#Registration page
@app.route("/register", methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.sManager.data: 
            if createAccReq(form.username.data, form.email.data, form.password.data):
                flash(f'Account approval for {form.username.data} sent to admin!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Registration Unsuccessful. Please try again', 'danger')

        elif form.submit.data:
            if createUser(form.username.data, form.email.data, form.password.data):
                flash(f'Account created for {form.username.data}!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Registration Unsuccessful. Please try again', 'danger')


    return render_template("register.html", title = 'Register', form = form)


#Login page
@app.route("/login", methods=['GET','POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = userValidate(form.email.data, form.password.data)
        usertype = user[0]
        global userid

        if usertype == 'admin':
            flash('you have been logged in admin!','success')
            userid = user[1]
            return redirect("/admin")
        elif usertype =='norm':
            flash('you have been logged in shopper!','success')
            userid = user[1]
            return redirect("/user")
        elif usertype == 'manager':
            flash('you have been logged in manager!','success')
            userid = user[1]
            return redirect("/manager")
        else:
            flash('Login Unsuccessful. Please try again', 'danger')
    
    return render_template("login.html", title = 'Login', form = form)

@app.route("/searchStart", methods=['GET','POST'])
def searchStart():
    form = searchForm()

    if form.validate_on_submit():
        flash(f'search results for {form.search.data} fetched!','success')
        path = "/search?id="+form.search.data
        return redirect(path)
    
    return render_template("searchStart.html", title = 'Search', form = form)


@app.route("/search", methods=['GET','POST'])
def search():
    form = searchForm()
    id = request.args["id"]
    all = searchKey(id)

    if form.validate_on_submit():
        flash(f'search results for {form.search.data} fetched!','success')
        path = "/search?id="+form.search.data
        return redirect(path)
    
    return render_template("search.html", title = 'Search', form = form, all = all)


#******************************************************************
#                          Admin Pages
#******************************************************************

#Home page
@app.route("/admin", methods=['GET','POST'])
def adminHome():
    items = viewItems()
    approvals = getApp()
    print(approvals)
    return render_template("adminHome.html", items = items, approvals = approvals, user = "admin")


#add a new Category
@app.route("/newCategory", methods=['GET','POST'])
def newCategory():
    form = newCategoryForm()
    user = request.args["user"]
    if form.validate_on_submit():
    
        if newCat(form.catName.data):
            flash(f'category added: {form.catName.data}!', 'success')
            if user == "admin":
                return redirect('/admin')
            elif user == "manager":
                return redirect("/manager")
        else:
            flash('Unsuccesful', 'danger')

    return render_template("newCategory.html", title = 'New Category', form = form)


#Add a new Item
@app.route("/newItem", methods=['GET','POST'])
def newItem():
    form = newItemForm()
    user = request.args["user"]
    category = str(request.args["catitem"])
    catName = fetchCatName(category)
    
    if form.validate_on_submit():
        item =[ form.itemName.data, form.price.data, form.stock.data ]
        
        if addItem(item, category):
            flash(f'item added: {form.itemName.data}!', 'success')
            if user == "admin":
                return redirect('/admin')
            elif user == "manager":
                return redirect("/manager")
        else:
            flash('Unsuccesful', 'danger')

    return render_template("newItem.html", title = 'New Item', form = form, name = catName)


#common page for editing a product ( fork page)
@app.route("/editPage", methods=['GET','POST'])
def editPage():
    id = request.args["id"]
    user = request.args["user"]
    item = fetchItem(id)
    
    return render_template("editPage.html", item = item, user = user)
    

#Edit the price of the product    
@app.route("/editPrice", methods=['GET','POST'])
def editPrice():
    id = request.args["id"]
    user = request.args["user"]
    item = fetchItem(id)
    form = editPriceForm() 
    
    if form.validate_on_submit():
    
        if form.submit.data:
    
            if editItemPrice(id, form.quantity.data):
                flash('item edited!', 'success')
                if user == "admin":
                    return redirect('/admin')
                elif user == "manager":
                    return redirect("/manager")
    
        elif form.back.data:
            if user == "admin":
                return redirect('/admin')
            elif user == "manager":
                return redirect("/manager")
    
    return render_template("editPrice.html", title = 'Edit Items', item = item, form = form )


#Edit stock amount of product
@app.route("/edit", methods=['GET','POST'])
def edit():
    id = request.args["id"]
    user = request.args["user"]
    item = fetchItem(id)
    form = editForm() 
    
    if form.validate_on_submit():
    
        if form.submit.data:
    
            if editItem(id, form.quantity.data):
                flash('item edited!', 'success')
                if user == "admin":
                    return redirect('/admin')
                elif user == "manager":
                    return redirect("/manager")
        elif form.delete.data:
    
            if deleteItem(id):
                flash('item edited!', 'success')
                if user == "admin":
                    return redirect('/admin')
                elif user == "manager":
                    return redirect("/manager")
        elif form.back.data:
            if user == "admin":
                return redirect('/admin')
            elif user == "manager":
                return redirect("/manager")
    
    return render_template("edit.html", title = 'Edit Items', item = item, form = form )


#page to show summary of products bought
@app.route("/summary", methods=['GET','POST'])
def summary():

    return render_template("summary.html")


@app.route("/viewRequest", methods=['GET','POST'])
def viewRequest():
    id = request.args["id"]
    form = approveForm()
    req = viewReq(id)
    
    if form.validate_on_submit():
        if form.approveBtn.data:
            type = str(req['reqtype'])
            if type == "NewManager":
                name = req['uName']
                createUser(req['uName'], req['uEmail'], req['uPass'], 2)
                delRequest(int(req['id']))
                flash(f'Account created for {name}!', 'success')
                return redirect(url_for('adminHome'))
            elif type == "DeleteCat":
                delCategory(id)
                flash('category deleted !', 'success')
                delRequest(int(req['id']))
                return redirect(url_for('adminHome'))

        elif form.rejectBtn.data:
            delRequest(id)
            flash(f'Request rejected!', 'success')
            return redirect(url_for('adminHome'))
            
    return render_template("request.html", req = req, form = form)

@app.route("/deleteCategory", methods=['GET','POST'])
def deleteCategory():
    id = request.args["id"]
    form = confirmForm()
    cat = fetchCat(id)
    if form.validate_on_submit():
        if form.yesBtn.data:
            if deleteCatReq(id):
                flash(f'Request sent to admin for deletion', 'success')
                return redirect(url_for('adminHome'))
        elif form.backBtn.data:
            return redirect(url_for('adminHome'))

    return render_template("deleteCategory.html", cat = cat, form = form)

#******************************************************************
#                          Manager Pages
#******************************************************************
#Home page
@app.route("/manager", methods=['GET','POST'])
def managerHome():
    global userid
    items = viewItems()
    
    return render_template("manHome.html", items = items, user = "manager")

# Simulated data for the CSV file
data = viewReport()

def generate_csv():
    filename = 'report.csv'
    with open(filename, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(data)

@app.route("/report", methods=['GET','POST'])
def index():
    print("before generate")
    form = GenerateReportForm()
    if form.validate_on_submit():
        if generate():
            flash('Report sent to manger via mail!', 'success')
            return redirect('/manager')
    return render_template('index.html', form = form)


def generate():

    print("before report")
    generate_csv()
    print("report generated")
    global userid
    manEmail = str(fetchMail(userid))
    with app.open_resource('report.csv') as attachment:
        print("i got here")
        msg = Message('CSV Report', sender='grocerystore031@gmail.com', recipients=[manEmail])
        msg.body = 'Please find the CSV report attached.'
        msg.attach('report.csv', 'text/csv', attachment.read())
        print("this is just before sending the mail")
        mail.send(msg)
    
    return True

#******************************************************************
#                          User Pages
#******************************************************************
import json


#home page
@app.route("/user", methods=['GET','POST'])
def home():
    
    myDict = {}

    myDict['vlist'] = viewItems()

    json_data = json.dumps(myDict)
    redis_client.setex('my_data',3600, json_data)
    
    json_data_from_redis = redis_client.get('my_data')

    if json_data_from_redis:
    # Convert the JSON-encoded string back to a dictionary
        retrieved_data = json.loads(json_data_from_redis.decode('utf-8'))

    items = retrieved_data['vlist']

    scheduler = BackgroundScheduler()
    scheduler.start()

    def send_daily_email():
        with app.app_context(): 
            users = fetchusers()

            for user in users:
                subject = "Daily Reminder!"
                recipient = user['email']
                message_body = "Hi "+user['userName']+", \n"
                count = itemsInCart(userid)
                if count == 0:
                    message_body += "There are no items in your cart. Shop now!"
                else:
                    message_body += "there are "+ str(count) + "item(s) in your cart. shop now!"

                message = Message(
                    subject=subject,
                    recipients=[recipient],
                    body=message_body,
                    sender='grocerystore031@gmail.com'
                )

                try:
                    mail.send(message)
                    print("Email sent successfully") 
                except Exception as e:
                    print("********", str(e))


    scheduler.add_job(send_daily_email, 'interval', seconds=30)

    def send_monthly_email():
        with app.app_context(): 
            users = fetchusers()

            for user in users:
                subject = "monthly Reminder!"
                recipient = user['email']
                message_body = "Hi "+user['userName']+", \n Here is your monthy activity report\n"
                message_body += "you have shopped with us "+str(user['shopCount'])+" time(s) \n"
                message_body += "you have spent a total of "+str(user['total'])+" Rs \n"
                userReset(user['id'])

                message = Message(
                    subject=subject,
                    recipients=[recipient],
                    body=message_body,
                    sender='grocerystore031@gmail.com'
                )

                try:
                    mail.send(message)
                    print("Email sent successfully") 
                except Exception as e:
                    print(str(e))
    
    scheduler.add_job(send_monthly_email, 'interval', seconds = 30)
    
    return render_template("home.html", items = items, message = "Welcome to The Grocery Store")


# Add an item to cart
@app.route("/addItem", methods=['GET','POST'])
def addCartItem():
    id = request.args["id"]
    item = fetchItem(id)
    form = addItemForm() 
    global userid
    userid = int(userid)
    if form.validate_on_submit():
        print(userid)
        if addToCart(id, form.quantity.data, userid):
            flash('item added!', 'success')
            return redirect("/user")
        else:
            flash('Sufficient items not available in stock. Please try again', 'danger')


    return render_template("addItem.html", title = 'Add Item', item = item, form = form)


#View items in the cart
@app.route("/cart", methods=['GET','POST'])
def cart():
    global userid
    items = viewCart(userid)
    form = buyForm() 
    total = findTotal(userid)
    
    if form.validate_on_submit():
    
        if form.buy.data:
    
            if buyItems(userid):
                flash('items bought!', 'success')
                return redirect(url_for('fin'))
        elif form.back.data:
            return redirect(url_for('home'))

    return render_template("cart.html", title = 'cart', items = items, form = form, cartLen = len(items), total = total)



#edit the item in the cart
@app.route("/editCart", methods=['GET','POST'])
def editItems():
    id = request.args["id"]
    item = fetchCartItem(id)
    form = editCartForm() 
    global userid
    
    if form.validate_on_submit():
    
        if form.submit.data:
            global userid
            if editCart(id, form.quantity.data, userid):
                flash('item edited!', 'success')
                return redirect(url_for('cart'))
    
        if form.back.data:
            return redirect(url_for('cart'))
    
        if form.delete.data:
    
            if deleteCart(id):
                
                flash('item removed', 'success')
                return redirect(url_for('cart'))
    
    return render_template("editCart.html", title = 'Edit Items', item = item, form = form )


#End page
@app.route("/thankyou", methods=['GET','POST'])
def fin():
    return render_template("end.html", title = 'Thankyou!')

#********************************************************
#                       Test 
#*********************************************************


if __name__ == '__main__':
    app.run(debug = True)