from ntpath import join
from flask import *
from flask_mail import *
from random import *
import requests
import json
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SelectField
from passlib.hash import sha256_crypt
from functools import wraps
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_mail import Mail, Message
import timeit
import datetime
import os
from wtforms.fields.html5 import EmailField
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/image/product'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

# Config MySQL
mysql = MySQL()
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'canteen'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize the app for use with this MySQL class
mysql.init_app(app)
mail = Mail(app)

# config mail

app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = 'jharahul1195@gmail.com'
app.config['MAIL_PASSWORD'] = 'bilfznveikqihssr'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, *kwargs)
        else:
            return redirect(url_for('login'))

    return wrap


def not_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return redirect(url_for('index'))
        else:
            return f(*args, *kwargs)

    return wrap


def is_admin_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin_logged_in' in session:
            return f(*args, *kwargs)
        else:
            return redirect(url_for('admin_login'))

    return wrap


def not_admin_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin_logged_in' in session:
            return redirect(url_for('admin'))
        else:
            return f(*args, *kwargs)

    return wrap


def wrappers(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)

    return wrapped

# Home page
@app.route('/')
def index():

    return render_template('home.html')


# Home page
@app.route('/canteen')
@is_logged_in
def index_login():

    cur = mysql.connection.cursor()
    cur.execute('SELECT `category` FROM `products` GROUP BY category')
    cat1 = cur.fetchall()
    cur.execute('SELECT * FROM ( SELECT *, ROW_NUMBER() OVER (PARTITION BY category Order by price DESC) AS Sno FROM products )RNK WHERE Sno <=4 ')
    product = cur.fetchall()

    cur.close()

    return render_template('user/home.html', cat1=cat1, product=product, show_predictions_modal=True)


# User registration form


class RegisterForm(Form):
    selectform = SelectField('', [validators.DataRequired()],
                             choices=[('1', 'Student'),
                                      ('2', 'Staff')], render_kw={'style': 'font-size:18px; padding:0 50px; outline:none;border-radius:5px;line-height:1;'})
    name = StringField('', [validators.length(min=3, max=50)],
                       render_kw={'autofocus': True, 'placeholder': 'Full Name'})
    username = StringField('', [validators.length(min=3, max=25)], render_kw={
                           'placeholder': 'Username'})
    email = EmailField('', [validators.DataRequired(), validators.Email(), validators.length(min=4, max=25)],
                       render_kw={'placeholder': 'Email'})
    password = PasswordField('', [validators.length(min=3), validators.EqualTo('cnf_password', message='Passwords must match')],
                             render_kw={'placeholder': 'Password'})
    cnf_password = PasswordField('', [validators.length(min=3)],
                                 render_kw={'placeholder': 'Confirm Password'})
    mobile = StringField('', [validators.length(min=10, max=11)], render_kw={
                         'placeholder': 'Mobile'})

 # Create Login Form


# Register Function
# user registration
@app.route('/register', methods=['GET', 'POST'])
@not_logged_in
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        select = dict(form.selectform.choices).get(form.selectform.data)
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        cnf_password = form.cnf_password.data
        mobile = form.mobile.data
        code = randint(000000, 999999)
        status = 'Not Verified'

        # Create Cursor
        cur = mysql.connection.cursor()
        email_check = cur.execute(
            "SELECT * FROM users WHERE email =%s", [email])
        mobile_check = cur.execute(
            "SELECT * FROM users WHERE mobile =%s", [mobile])

        if email_check > 0 and mobile_check > 0:
            flash(f"{email} and {mobile} Already Exist", 'danger')
            return redirect(url_for('register'))
        elif mobile_check > 0:
            flash(f"{mobile} Already Exist", 'danger')
            return redirect(url_for('register'))
        elif email_check > 0:
            flash(f"{email} Already Exist", 'danger')
            return redirect(url_for('register'))

        else:

            cur.execute("INSERT INTO users(category,  email,name, username, password,code, status, mobile) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
                                      (select, email, name, username, password, code, status, mobile))
            # Commit cursor
            mysql.connection.commit()

            # Close Connection
            cur.close()
            try:
                msg = Message(
                'OTP', sender='jharahul1195@gmail.com', recipients=[email])
                msg.body = f' Registered as {select} code is {code} '
                mail.send(msg)
                flash('Verification Requird', 'success')
                return redirect(url_for('validate'))
            except:
                return render_template('register.html', form=form)

    return render_template('register.html', form=form)

# OTP validation form


class ValidationForm(Form):
    otp_field = PasswordField('Please Enter OTP Number')

# OTP validation
@app.route('/validate', methods=['GET', 'POST'])
def validate():
    
    form = ValidationForm(request.form)
    if request.method == 'POST' and form.validate():
        user_otp = form.otp_field.data
        cur = mysql.connection.cursor()
        code_check = cur.execute(
            "SELECT * FROM users WHERE code =%s", [user_otp])

        if code_check > 0:
            session['info'] = ""

            code = 0
            status = 'varified'
            update_otp = cur.execute("UPDATE users SET code=%s, status=%s WHERE code=%s",
                                        (code, status, user_otp))
            flash("varification successful", "success")
            return redirect(url_for("login"))

        flash("failure, OTP does not match", 'danger')
        return redirect(url_for('validate'))
    return render_template('Verify.html', form=form)
   


class LoginForm(Form):

    email = EmailField('', [validators.DataRequired(), validators.Email(), validators.length(min=4, max=25)],
                       render_kw={'placeholder': 'Email'})
    password = PasswordField('', [validators.length(min=3)],
                             render_kw={'placeholder': 'Password'})


# User Login
@app.route('/login', methods=['GET', 'POST'])
@not_logged_in
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        # GEt user form

        email = form.email.data
        # password_candidate = request.form['password']
        password_candidate = form.password.data

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute(
            "SELECT * FROM users WHERE email=%s", [email])

        if result > 0:
            # Get stored value
            data = cur.fetchone()
            username = data['username']
            password = data['password']
            uid = data['id']
            name = data['name']
            code = data['code']
            status = data['status']
            mobile = data['mobile']

            # Compare password
            if sha256_crypt.verify(password_candidate, password):
                # passed
                session['email'] = email
                if status == 'varified':
                    session['logged_in'] = True
                    session['uid'] = uid
                    session['s_name'] = name
                    session['email'] = email
                    session['mobile'] = mobile 


                    x = '1'
                    cur.execute(
                        "UPDATE users SET online=%s WHERE id=%s", (x, uid))

                    return redirect(url_for('index_login'))
                flash(
                    f"It's look like you haven't still verify your email - {email}")
                return redirect(url_for("validate"))

            else:
                flash('Incorrect password', 'danger')
                return render_template('login.html', form=form)

        else:
            flash('Email not found! need to register first', 'danger')
            # Close connection
            cur.close()
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)


# User Logout
@app.route('/out')
def logout():
    if 'uid' in session:
        # Create cursor
        cur = mysql.connection.cursor()
        uid = session['uid']
        x = '0'
        cur.execute("UPDATE users SET online=%s WHERE id=%s", (x, uid))
        session.clear()
        flash('You are logged out', 'success')
        return redirect(url_for('index'))
    return redirect(url_for('login'))


# forgot password
# password Email Field
class PasswordemailForm(Form):
    email = EmailField('', [validators.DataRequired(), validators.Email(), validators.length(min=4, max=25)],
                       render_kw={'placeholder': 'Email'})

# New Password form


class NewpasswordForm(Form):

    newpassword = PasswordField('', [validators.length(min=3), validators.EqualTo('cnf_newpassword', message='Passwords must match')],
                                render_kw={'placeholder': 'Password'})
    cnf_newpassword = PasswordField('', [validators.length(min=3)],
                                    render_kw={'placeholder': 'Confirm Password'})

@app.route('/Password_email', methods=['GET', 'POST'])
def forgot_email():
    form = PasswordemailForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        code = randint(000000, 999999)
        # Create Cursor
        cur = mysql.connection.cursor()
        email_check = cur.execute(
            "SELECT * FROM users WHERE email =%s", [email])
        session['email'] = email
        if email_check > 0:

            insert_data = cur.execute(
                "UPDATE users SET code=%s WHERE email=%s",
                (code, email))

            # Commit cursor
            mysql.connection.commit()

            # Close Connection
            cur.close()

            msg = Message(
                'OTP', sender='prouser.rahul.01@gmail.com', recipients=[email])
            msg.body = str(code)
            mail.send(msg)
            info = flash('Verification Requird', 'success')
            return redirect(url_for('verifyotp'))
        else:
            flash('Email does not Exist', "danger")
    return render_template('forgot_password.html', form=form)



# forgot password email


# Reset Password OTP verification
@app.route('/Verify_ otp', methods=['GET', 'POST'])
def verifyotp():
    form = ValidationForm(request.form)
    if request.method == 'POST' and form.validate():
        user_otp = form.otp_field.data
        cur = mysql.connection.cursor()
        code_check = cur.execute(
            "SELECT * FROM users WHERE code =%s", [user_otp])

        if code_check > 0:
            code = 0
            update_otp = cur.execute("UPDATE users SET code=%s WHERE code=%s",
                                     (code, user_otp))
            flash("varification successful", "success")
            return redirect(url_for("newpassword"))

        flash("failure, OTP does not match", 'danger')
        return redirect(url_for('verify_otp'))

    return render_template('Verify.html', form=form)


# Forgot password
@app.route('/newpassword', methods=['GET', 'POST'])
def newpassword():
    form = NewpasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        newpassword = sha256_crypt.encrypt(str(form.newpassword.data))
        cnf_newpassword = form.cnf_newpassword.data
        email = session['email']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET password=%s WHERE email=%s",
                    (newpassword, email))
        flash("varification successful", "success")
        return redirect(url_for("login"))

    return render_template('new_password.html', form=form)


# feedback
@app.route('/feedback', methods=['POST'])
def feedback():
    if request.method == 'POST':

        email = request.form.get('email')

        # database connect
        cur = mysql.connection.cursor()
        sub = cur.execute("SELECT * FROM feedback WHERE email =%s", [email])
        if sub > 0:
            flash("You Already Subscribed", 'success')
            return redirect(url_for('index'))
        else:
            cur.execute("INSERT INTO feedback(email) VALUES( %s)",
                        (email,))

            # Commit cursor
            mysql.connection.commit()

            # Close Connection
            cur.close()

            msg = Message(
                'OTP', sender='prouser.rahul.01@gmail.com', recipients=[email])
            msg.body = 'successful'
            mail.send(msg)
            flash('successfull', 'success')
            return redirect(url_for('index'))
    flash('try again', 'danger')
# User Profile


@app.route('/user/profile')
def profile():

    return render_template('user/index.html')

# Admin Login
@app.route('/admin_login', methods=['GET', 'POST'])
@not_admin_logged_in
def admin_login():
    if request.method == 'POST':
        # GEt user form
        username = request.form['email']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM admin WHERE email=%s", [username])

        if result > 0:
            # Get stored value
            data = cur.fetchone()
            password = data['password']
            uid = data['id']
            name = data['firstName']

            # Compare password
            if sha256_crypt.verify(password_candidate, password):
                # passed
                session['admin_logged_in'] = True
                session['admin_uid'] = uid
                session['admin_name'] = name

                return redirect(url_for('admin'))

            else:
                flash('Incorrect password', 'danger')
                return render_template('admin/login.html')

        else:
            flash('Username not found', 'danger')
            # Close connection
            cur.close()
            return render_template('admin/login.html')
    return render_template('admin/login.html')

# Admin Logout
@app.route('/admin_out')
def admin_logout():
    if 'admin_logged_in' in session:
        session.clear()
        return redirect(url_for('admin_login'))
    return redirect(url_for('admin'))

# Admin Index


@app.route('/admin')
@is_admin_logged_in
def admin():
    curso = mysql.connection.cursor()
    num_rows = curso.execute("SELECT * FROM products")
    result = curso.fetchall()
    users_rows = curso.execute("SELECT * FROM users")
    return render_template('admin/all_product.html', result=result, row=num_rows, users_rows=users_rows)


@app.route('/users')
@is_admin_logged_in
def users():
    curso = mysql.connection.cursor()
    num_rows = curso.execute("SELECT * FROM products")
    users_rows = curso.execute("SELECT * FROM users")
    result = curso.fetchall()
    return render_template('admin/all_user.html', result=result, row=num_rows,
                           users_rows=users_rows)

# Admin Add Product
@app.route('/admin_add_product', methods=['GET', 'POST'])
@is_admin_logged_in
def admin_add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        available = request.form['available']
        category = request.form['category']
        item = request.form['item']
        code = request.form['code']
        file = request.files['picture']
        # Create Cursor
        pic = file.filename
        photo = pic.replace("'", "")
        picture = photo.replace(" ", "_")
        if picture.lower().endswith(('.png', '.jpg', '.jpeg')):
            save_photo = photos.save(file, folder=category)
            if save_photo:
                # Create Cursor
                curs = mysql.connection.cursor()
                curs.execute("INSERT INTO products(pName,price,description,available,category,item,pCode,picture)"
                             "VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
                             (name, price, description, available, category, item, code, picture))
                mysql.connection.commit()
                curs.close()
                flash("added successfully", "success")
                return redirect(url_for('admin_add_product'))

            else:
                flash("not saved")
        else:
            flash("not matched")

    else:
        return render_template('admin/add_product.html')

# Edit product
@app.route('/edit_product', methods=['POST', 'GET'])
@is_admin_logged_in
def edit_product():
    if 'id' in request.args:
        product_id = request.args['id']
        curso = mysql.connection.cursor()
        res = curso.execute(
            "SELECT * FROM products WHERE id=%s", (product_id,))
        product = curso.fetchall()
        list1 = ['HOT-BEVERAGES', 'DRINK', 'SANDWICHES', 'PARATHAS', 'SNACKS',
                 'COLD BEVERAGES', 'CHATS', 'NOODLES', 'MOMOS', 'FRID RICES']

        if res:

            if request.method == 'POST':
                name = request.form.get('name')
                price = request.form['price']
                description = request.form['description']
                available = request.form['available']
                category = request.form['category']
                item = request.form['item']
                code = request.form['code']
                file = request.files['picture']

                # Create Cursor
                if name and price and description and available and category and item and code and file:
                    pic = file.filename
                    photo = pic.replace("'", "")
                    picture = photo.replace(" ", "")
                    if picture.lower().endswith(('.png', '.jpg', '.jpeg')):
                        file.filename = picture
                        save_photo = photos.save(file, folder=category)
                        if save_photo:

                            # Create Cursor
                            cur = mysql.connection.cursor()
                            exe = curso.execute(
                                "UPDATE products SET pName=%s, price=%s, description=%s, available=%s, category=%s, item=%s, pCode=%s, picture=%s WHERE id=%s",
                                (name, price, description, available, category, item, code, picture, product_id))
                            # Commit cursor
                            mysql.connection.commit()
                            cur.close()

                            flash('Data updated', 'success')
                            return redirect(url_for('admin'))
                        else:
                            flash('Please Upload Image', "danger")
                            return redirect(render_template('admin/edit_product.html'))
                    else:
                        flash('File not support', 'danger')
                        return render_template('admin/edit_product.html', product=product, list1=list1)
                else:
                    flash('Fill all field', 'danger')
                    return render_template('admin/edit_product.html', product=product, list1=list1)
            else:
                return render_template('admin/edit_product.html', product=product, list1=list1)
        else:
            return redirect(url_for('admin_login'))
    else:
        return redirect(url_for('admin_login'))


@app.route('/View_Product/product.html')
@is_logged_in
def view_product():
    # Create cursor
    if 'category' in request.args:
        product_category = request.args['category']
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT category FROM products  WHERE category=%s group by category", (product_category,))
        category = cur.fetchall()
        res = cur.execute(
            "SELECT * FROM products WHERE category=%s", (product_category,))
        product = cur.fetchall()
        cur.close()
        flash(f"Product Related to {product_category}")
        return render_template('user/product.html', product=product, category=category)
    else:
        return redirect(url_for('index_login'))
    # if 'view' in request.args:
    #     product_id = request.args['view']
    #     curso = mysql.connection.cursor()
    #     curso.execute("SELECT * FROM products WHERE id=%s", (product_id,))
    #     product_view = curso.fetchall()
    #     return render_template('view_product_id.html', product_view=product_view)
    # elif 'order' in request.args:
    #     product_id = request.args['order']
    #     curso = mysql.connection.cursor()
    #     curso.execute("SELECT * FROM products WHERE id=%s", (product_id,))
    #     product_order = curso.fetchall()
    #     return render_template('order_product.html')
    # elif 'cart' in request.args:
    #     product_id = request.args['cart']
    #     curso = mysql.connection.cursor()
    #     curso.execute("SELECT * FROM products WHERE id=%s", (product_id,))
    #     product_cart = curso.fetchall()
    #     flash("Added Food Successfully", 'success')
    #     return render_template('cart_product.html')


@app.route('/View_Product_id/view_product_id.html')
@is_logged_in
def view_product_id():
    # Create cursor
    if 'id' in request.args:
        product_id = request.args['id']
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM products  WHERE id=%s", (product_id,))
        id = cur.fetchall()
        # product_price = id[0]["price"]
        product_name = id[0]["pName"]
        cur.close()
        flash(f"""Product Related to {product_name}""")
        return render_template('user/view_product_id.html', id=id)
    else:
        return redirect(url_for('index_login'))


@app.route('/order_product/order_detail', methods=['GET', 'POST'])
@is_logged_in
def order():
    if 'uid' in session:
        uid = session['uid']
        student_name = session['s_name'] 
        email = session['email']
        mobile = session['mobile'] 
        # cur = mysql.connection.cursor()
        # cur.execute("SELECT * FROM users WHERE id=%s", (uid,))
        # user_data = cur.fetchone()
        # name = 

        if 'order' in request.args:
            product_id = request.args['order']
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM products WHERE id=%s', (product_id,))
            order_item = cur.fetchall()
            product_name = order_item[0]["pName"]
            product_price = order_item[0]["price"]
            # total_price = product_price*total_q
            
            cur.close()
            flash(f"You are ordering {product_name}")
            return render_template('user/indi_order.html', order_item=order_item)
        else:
            flash('Something went wrong please try again','dangar')
            return render_template('/canteen')
        


@app.route('/canteen/cart.html')
@is_logged_in
def cart():

    return render_template('user/cart.html')

if __name__ == '__main__':
    app.run(debug=True)