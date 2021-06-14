from flask import Flask, render_template, request,redirect,url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_login import login_user, current_user, logout_user, login_required
import pygal

import string
import random

LETTERS = string.ascii_letters
NUMBERS = string.digits  
PUNCTUATION = string.punctuation 

from settings.config import Development, Staging, Production

# import db connection
from settings.db_connect import conn

app = Flask(__name__)
app.config.from_object(Staging)
db = SQLAlchemy(app)
login_manager = LoginManager(app)

from models.inventory import InventoryModel
from models.sales import SalesModel
from models.stock import StockModel
from models.users import UsersModel
from models.contact import ContactModel
from models.contactsales import ContactsalesModel
from models.company import CompanyModel

# import sentry_sdk
# from flask import Flask
# from sentry_sdk.integrations.flask import FlaskIntegration

# sentry_sdk.init(
#     dsn="https://9ab1d05348c94175b10a4465b301d859@o490237.ingest.sentry.io/5556864",
#     integrations=[FlaskIntegration()],
#     traces_sample_rate=1.0
# )

# # @app.route('/debug-sentry')
# # def trigger_error():
# #     division_by_zero = 1 / 0

# app = Flask(__name__)

from functools import wraps
def stock_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role != "Super Manager" and current_user.role != "Stock Manager":
            print(current_user.role)
            flash("You are not authorized to undertake this task", "warning")
            return redirect(url_for('dashboard'))
            
        else:
            return f(*args, **kwargs)
    return wrap

def sale_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role != "Super Manager" and current_user.role != "Sales Rep":
            print(current_user.role)
            flash("You are not authorized to undertake this task", "warning")
            return redirect(url_for('dashboard'))
            
        else:
            return f(*args, **kwargs)
    return wrap

def super_manager_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role != "Super Manager":
            print(current_user.role)
            flash("You are not authorized to undertake this task", "warning")
            return redirect(url_for('dashboard'))
            
        else:
            return f(*args, **kwargs)
    return wrap

def password_generator(length=12):
    printable = f'{LETTERS}{NUMBERS}{PUNCTUATION}'
    printable = list(printable)
    random.shuffle(printable)
    random_password = random.choices(printable, k=length)
    random_password = ''.join(random_password)
    return random_password

def hash_password(random_password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', random_password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')
 
def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                  provided_password.encode('utf-8'), 
                                  salt.encode('ascii'), 
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password



import africastalking
def send_sms(phoneNumber, email, random_password):    
    # Initialize SDK
    username = "theurikenneth"    # use 'sandbox' for development in the test environment
    api_key = "f8bd4c21fd947d077a16c4737a8658867992ef7890ccca06060ee03ef53e1eac"      # use your sandbox app API key for development in the test environment
    africastalking.initialize(username, api_key)
    # Initialize a service e.g. SMS
    sms = africastalking.SMS
    # Use the service synchronously
    phone=[]
    phone.append('+254'+phoneNumber)
    response = sms.send("Please login to your Zaplabs account with email: "+email + " and password:"+random_password, phone)
    print(response)


@app.before_first_request
def create_table():
    print("Hello")
    db.create_all()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        name=request.form['name']
        email=request.form['email']
        textarea=request.form['textarea']

        contact=ContactModel(name=name, email=email, textarea=textarea)
        contact.insertRecord()

        flash("Message Sent Successfully!", "success")
    return render_template('contact.html')

@app.context_processor
def utility_processor():
    def available_stock(inventory_id):
        record = InventoryModel.query.filter_by(id=inventory_id).first()
        total_stock = sum(list(map(lambda obj: obj.quantity, record.stock)))
        total_sales = sum(list(map(lambda obj: obj.quantity, record.sales)))
        return total_stock-total_sales
    return dict(available_stock=available_stock)

@app.route('/inventories', methods=['GET','POST'])
@login_required
def inventories():

    # Open a cursor to perform database operations
    """cur = conn.cursor()
    cur.execute("SELECT id,name,inventory_type,buying_price,selling_price FROM inventories")
    records =cur.fetchall()"""

    all_inventories = InventoryModel.fetchAllInventories()
    print(all_inventories)
    print(type(all_inventories))

    if request.method =='POST':
        name = request.form['name']
        inventory_type = request.form['inventory_type']
        buying_price = request.form['buying_price']
        selling_price = request.form['selling_price']

        me = InventoryModel(name=name, inventory_type=inventory_type, buying_price=buying_price, selling_price=selling_price)
        me.insertRecord()

        """cur.execute("INSERT INTO inventories (name, inventory_type, buying_price, selling_price) VALUES(%s,%s,%s,%s)",(name,inventory_type,buying_price,selling_price))
        # Commit your changes in the database
        conn.commit()"""
        
        flash("Record has been successfully created","success")
        return redirect(url_for('inventories'))
       
    return render_template('inventories.html',all_inventories=all_inventories)

@app.route('/inventories/<inventory_id>/stock', methods=['GET','POST'])
@login_required
@stock_required
def add_stock(inventory_id):
    
    if request.method =='POST':
        quantity = request.form['quantity']

        me=StockModel(quantity=quantity, inventory_id=inventory_id)
        me.insertRecord()

        flash("Stock has been successfully added","success")
        return redirect(url_for('inventories'))

@app.route('/inventories/<inventory_id>sale', methods=['GET','POST'])
@login_required
@sale_required
def add_sale(inventory_id):

    if request.method =='POST':
        quantity = request.form['quantity']

        me=SalesModel(quantity=quantity, inv_id=inventory_id)
        me.insertRecord()

        flash("Sale has been successfully added","success")
        return redirect(url_for('inventories'))

@app.route("/inventories/<inventory_id>view_sales", methods=['GET','POST'])
@login_required
@sale_required
def view_sales(inventory_id):
    inventory_details=InventoryModel.query.filter_by(id=inventory_id).first()
    #inventory_sales=SalesModel.query.filter_by(id=inventory_id).first()
    inventory_sales=inventory_details.sales
    return redirect(url_for('inventories'))

@app.route('/inventories/<inventory_id>edit', methods=['POST'])
@login_required
@stock_required
def edit_inventory(inventory_id):

    if request.method == 'POST':
        name = request.form['name']
        inventory_type = request.form['inventory_type']
        buying_price = request.form['buying_price']
        selling_price = request.form['selling_price']

        if InventoryModel.updateInventoryById(inventory_id=inventory_id, name=name, inventory_type=inventory_type, buying_price=buying_price, selling_price=selling_price):
            flash("Inventory has been successfully edited","success")
            return redirect(url_for('inventories'))

        else:
            flash("Could not update {{each.name}} inventory","danger")
            return redirect(url_for('inventories'))


@app.route('/inventories/<inventory_id>delete', methods=['POST'])
@login_required
@stock_required
def delete_inventory(inventory_id):
    record =InventoryModel.query.filter_by(id=inventory_id).first()
    if len(record.stock) > 0:
        flash("Inventory contains existing stock", "warning")
        return redirect(url_for('inventories'))
    
    """if len(record.sales) > 0:
        flash("Inventory contains existing sales", "warning")
        return redirect(url_for('inventories'))"""

    if record:
        db.session.delete(record)
        db.session.commit()
        flash("Successfully deleted","warning")
        
    else:
        flash("Error!! Operation unsuccessful", "warning")

    return redirect(url_for('inventories'))

@app.route('/delete_sale/<i_id>', methods=['POST'])
@login_required
@sale_required
def delete_sale(i_id):
    record =SalesModel.query.filter_by(id=i_id).first()

    if record:
        db.session.delete(record)
        db.session.commit()
        flash("Inventory successfully deleted","warning")
        return redirect(url_for('inventories'))
        
    else:
        flash("Error!! Operation Unsuccessful", "warning")
        return redirect(url_for('inventories'))


@app.route('/charts')
def charts():
    total_inventories = len(InventoryModel.fetchAllInventories()) 
    total_products = len(InventoryModel.query.filter_by(inventory_type="product").all())
    total_services =len(InventoryModel.query.filter_by(inventory_type="service").all())
    total_sales = len(SalesModel.fetchAllSales())

    pie_chart = pygal.Pie()
    pie_chart.title = 'Products vs Services'
    pie_chart.add('Products', total_products)
    pie_chart.add('Services', total_services)
    pie = pie_chart.render_data_uri()

    line_chart = pygal.Bar()
    line_chart.title = 'Products vs Services vs Inventories vs Sales'
    line_chart.x_labels = map(str, range(2020, 2022))
    line_chart.add('Products', total_products)
    line_chart.add('Services',  total_services)
    line_chart.add('Inventories', total_inventories)
    line_chart.add('Sales', total_sales)
    line_chart = line_chart.render_data_uri()

    return render_template('charts.html', total_inventories=total_inventories, total_products=total_products, total_services=total_services, total_sales=total_sales, chart=pie, line_chart=line_chart)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        company_name = request.form['company_name']
        company_location = request.form['company_location']
        fullName = request.form['fullName']
        emailAddress = request.form['emailAddress']
        code = request.form['code']
        phoneNumber = request.form['phoneNumber']
        role = request.form['role']
        password = request.form['password']
        if UsersModel.fetch_user_by_email(emailAddress=emailAddress):
            flash("The email address already exists", "warning")
            return redirect(url_for('register'))

        else:
            company = CompanyModel(company_name=company_name, company_location=company_location)
            db.session.add(company)
            db.session.commit()
            user = UsersModel(company_id=company.id, fullName=fullName, emailAddress=emailAddress, code=code, phoneNumber=phoneNumber, role=role, password=password)
            db.session.add(user)
            db.session.commit()
            
            flash("Your account has been created successfully", "success")
            return redirect(url_for('signin'))
    return render_template('register.html')

@app.route('/signin', methods=['GET','POST'])
def signin():
    if request.method == 'POST':
        emailAddress = request.form['emailAddress']
        password = request.form['password']
        user = UsersModel.query.filter_by(emailAddress=emailAddress, password=password).first()
        if user:
            login_user(user)
            session['company_id']=user.company_id
            session['company_name']=user.user.company_name
            flash("Login Successful", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Login Unsuccessful", "warning")       
    return render_template('signin.html')

@app.route('/logout')
def logout():
    logout_user()
    flash("You have logged out successfully", "success")
    return redirect(url_for('signin'))

@app.route('/add_user', methods=['GET','POST'])
@login_required
@super_manager_required
def add_user():
    if request.method == 'POST':
        fullName = request.form['fullName']
        emailAddress = request.form['emailAddress']
        code = request.form['code']
        phoneNumber = request.form['phoneNumber']
        role = request.form['role']
        password = password_generator()
        if UsersModel.fetch_user_by_email(emailAddress=emailAddress):
            flash("The email address already exists", "warning")
            return redirect(url_for('add_user'))

        elif UsersModel.fetch_user_by_phoneNumber(phoneNumber=phoneNumber):
            flash("The phone number already exists", "warning")
            return redirect(url_for('add_user'))

        else:
            user = UsersModel(company_id=session['company_id'], fullName=fullName, emailAddress=emailAddress, code=code, phoneNumber=phoneNumber, role=role, password=password)
            db.session.add(user)
            db.session.commit()
            send_sms(phoneNumber, emailAddress, password)
            
            flash("The account has been created successfully", "success")
            return redirect(url_for('dashboard'))
    return render_template('add_user.html')

@app.route('/remove_user', methods=['GET','POST'])
@login_required
@super_manager_required
def remove_user():
    if request.method == 'POST':
        fullName = request.form['fullName']
        emailAddress = request.form['emailAddress']

        if UsersModel.fetch_user_by_email(emailAddress=emailAddress):
            user = db.session.query(UsersModel).filter(emailAddress==emailAddress).first()
            #user = UsersModel(company_id=session['company_id'], fullName=fullName, emailAddress=emailAddress, code=code, phoneNumber=phoneNumber, role=role, password=password)
            db.session.delete(user)
            db.session.commit()
            
            #record_obj = db.session.query(Model).filter(Model.id==123).first()
            flash("The account has been removed successfully", "success")
            return redirect(url_for('dashboard'))

        else:
            flash("The email address does not exist", "warning")
            return redirect(url_for('remove_user'))

    return render_template('remove_user.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/contactsales', methods=['GET','POST'])
def contactsales():
    if request.method == 'POST':
        name=request.form['name']
        email=request.form['email']
        companyname=request.form['companyname']
        companysize=request.form['companysize']
        country=request.form['country']
        salesteamhelp=request.form['salesteamhelp']
        textarea=request.form['textarea']

        contactsales=ContactsalesModel(name=name, email=email, companyname=companyname, companysize=companysize, country=country, salesteamhelp=salesteamhelp, textarea=textarea)
        contactsales.insertRecord()

        flash("Message Sent to Sales Successfully!", "success")
    return render_template('contactsales.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/zaplabs-vs-manual')
def zaplabs_vs_manual():
    return render_template('zaplabs_vs_manual.html')

@app.route('/solutions')
def solutions():
    return render_template('solutions.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')