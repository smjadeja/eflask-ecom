# import statements
from flask import Flask, render_template, session, request, session,redirect,flash,g, url_for,Response
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import backref
from datetime import datetime, date
import os
import re
from werkzeug.utils import secure_filename

from uuid import uuid4
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

#app configs
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///buysell.db'
db = SQLAlchemy(app)

app.secret_key  = os.urandom(24)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'jfif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#models

# a = Usertype(role_name = 'buyer', role_desc= 'buyer cann buy from seller')
# b = User(first_name = 'first user', last_name='user1 lastname', date_of_birth=datetime(2020, 5, 17), email='jadeja@gmail.com', mobile = '5454545', balance=3000.00, password='pass123', address='this address', role= a)
# c = User(first_name = 'second user', last_name='user1 lastname', date_of_birth=datetime(2022, 5, 17), email='jadea@gmail.com', mobile = '5454545', balance=3000.00, password='pass123', address='this address', role= a)

# a.users.append(b)
# a.users.append(c)
# db.session.add(a)
# db.session.commit()



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def make_unique(string):
    ident = uuid4().__str__()
    return f"{ident}-{string}"

class Usertype(db.Model):
    __tablename__ = 'usertype'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(10), nullable=False)
    role_desc = db.Column(db.String(100), nullable=False)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name =  db.Column(db.String(30), nullable = False)
    last_name = db.Column(db.String(30), nullable = False)
    date_of_birth = db.Column(db.Date, nullable = False)
    email = db.Column(db.String(120),unique=True, nullable=False)
    mobile = db.Column(db.String(10), nullable=False)
    balance = db.Column(db.Float, nullable = False)
    password = db.Column(db.String(50), nullable = False)
    address = db.Column(db.String(120), nullable = False)
    role_id = db.Column(db.Integer, db.ForeignKey('usertype.id'), nullable=False)
    # role = db.relationship('Usertype', backref=db.backref('users', lazy=True))


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key = True)
    product_name = db.Column(db.String(10), nullable = False)
    product_desc = db.Column(db.String(30), nullable = False)
    product_img = db.Column(db.String(60), nullable = False)
    product_sell_price = db.Column(db.Float, nullable= False)
    product_cost_price = db.Column(db.Float, nullable = False)
    stock_unit = db.Column(db.Integer, nullable= False)
    created_by_user = db.Column(db.Integer, ForeignKey('user.id'))
    create_date = db.Column(db.Date, default=datetime.utcnow, nullable = False)
    is_deleted = db.Column(db.Boolean, nullable = False, default = 1)

class User_Purchase(db.Model):
    __tablename__ = 'user_purchase'
    id = db.Column(db.Integer,primary_key=True)
    purchase_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    total_unit = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    purchase_by_user = db.Column(db.Integer, ForeignKey('user.id'))
    purchase_from_user = db.Column(db.Integer, ForeignKey('user.id'))


# @app.route('/upload', methods = ['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         f = request.files['file']
#         # f.save(secure_filename(f.filename))
#         filename = secure_filename(f.filename)
#         f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         return 'file uploaded successfully'
#     return render_template('upload.html')

    


class UserView(MethodView):
    def get(self):
        if not g.username:
            roles = Usertype.query.all()
            return render_template('signup.html', role=roles)
        return redirect('/home')
    def post(self):    
            firstname = request.form['firstname']  
            for i in firstname:
                if i.isdigit():
                    return 'please enter valid first name'        
            lastname = request.form['lastname']
            for i in lastname:
                if i.isdigit():
                    return 'please enter valid lastname'
            mobile = request.form['mobile'] 
            if not mobile.isdigit():
                flash('please enter valid mobile number')   
                return Response('please enter valid number')
            if not len(mobile) == 10:
                return 'please enter 10 digit number'
            email = request.form['email']
            if not (re.fullmatch(regex, email)):
                return 'please enter valid email'                
            if User.query.filter_by(email=email).first():
                return 'email already exist'                
            password = request.form['password'] 
            if len(password) < 6:
                return 'please enter password more than 6 characters' 
            balance = request.form['balance']
            if not balance.isdigit():
                flash('please enter valid balance value')
                return redirect('/signup')
            if request.form['dateofbirth'] == "":
                return Response('incorrect date of birth')
            dateofbirth = request.form['dateofbirth'].split('-')
            year, month, day = dateofbirth
            address = request.form['address']
            role = request.form['user_role']
            user = User(first_name = firstname, last_name=lastname, date_of_birth=datetime(int(year), int(month), int(day)), email=email, mobile = '5454545', balance=float(balance), password=password, address=address, role_id=int(role))
            db.session.add(user)
            db.session.commit()
            flash('registered succesfully')
            return redirect('/')
 
user_view = UserView.as_view('user_view')

class LoginView(MethodView):
    def get(self):
        if g.username:
            return redirect('/home')
        return render_template('login.html')

    def post(self):
        email = request.form['email']   
        password = request.form['password']
        if not (re.fullmatch(regex, email)):
            flash('please enter valid email') 
            return redirect('/')  
        a = User.query.filter_by(email=email, password=password).first()
        if not a:
            flash('incorrect email or password')
            return redirect('/')
        session.pop('user', None)
        session['user'] = a.first_name
        session['id'] = a.id
        session['role_id'] = a.role_id
        return redirect('/home')

login_view = LoginView.as_view('login_view')

class Homeview(MethodView):
    def get(self):
        if g.username:
        # products = Product.query.all()
            user = User.query.filter_by(id=g.id).first()
            rolename = Usertype.query.get(g.role_id).role_name
            return render_template('products.html', user = user, rolename = rolename)
        return redirect('/')
Homeview = Homeview.as_view('Homeview')

class Productview(MethodView):
    def get(self):
        if g.username and g.role_id == 1:       
            prods = Product.query.filter_by(created_by_user=g.id, is_deleted = 1).all()
            return render_template('viewproduct.html', prods = prods, user= g.username, seller= g.role_id)
        elif g.username and g.role_id == 2:
            prods = Product.query.filter_by(is_deleted = 1).all()
            buyer = g.role_id 
            buyer_balance = User.query.get(g.id).balance
            print(buyer_balance)
            return render_template('viewproduct.html', prods = prods, buyer = buyer,buyer_balance = buyer_balance)
        return redirect('/')
product_view = Productview.as_view('product_view')

class AddProd(MethodView):
    def post(self):
        if g.username:
            prodname = request.form['prodname']
            prod_desc = request.form['prod_desc']
            sellprice = request.form['sellprice']
            costprice = request.form['costprice']
            stockunit = request.form['stockunit']
            print('stock unit')
            f = request.files['file']
            if not allowed_file(f.filename):
                return 'please upload valid image file'
            original_filename = secure_filename(f.filename)
            unique_filename = make_unique(original_filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                
             
            product = Product(product_name=prodname, product_desc = prod_desc,product_img=unique_filename,product_sell_price=sellprice, product_cost_price = costprice, stock_unit= stockunit, created_by_user= g.id)
            flash('product was added succesfully')
            db.session.add(product)
            db.session.commit()
            
            return redirect('/viewproduct')
        return redirect('/')

add_prod = AddProd.as_view('add_prod')

class EditView(MethodView):
    def get(self, id):
        if g.username and g.role_id == 1:
            prod = Product.query.get(id)
            return render_template('editproducts.html', prod = prod)
        return redirect('/')
    def post(self, id):
        if g.username and g.role_id == 1:
            prod = Product.query.get(id)
            prod.product_name = request.form['product']
            prod.product_desc = request.form['prod_desc']
            f = request.files['file']
            if not f:
                return 'no files'
            if f and allowed_file(f.filename):
                original_filename = secure_filename(f.filename)
                unique_filename = make_unique(original_filename)
                prod.product_img = unique_filename
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))

            prod.product_sell_price = request.form['sellprice']
            prod.product_cost_price = request.form['costprice']
            prod.stock_unit = request.form['stockunit']
            db.session.commit()
            return redirect('/viewproduct')
        return redirect('/')
edit_view = EditView.as_view('edit_view')


class SellHistory(MethodView):
    def get(self):
        if g.username and g.role_id == 1:
            sell_list = User_Purchase.query.filter_by(purchase_from_user=g.id).all()
            return render_template('sellhistory.html', sell_list = sell_list, Product = Product, User = User)
        return redirect('/')

sellhistory = SellHistory.as_view('sellhistroy')

class Orderhistory(MethodView):
    def get(self):
        if g.username:
            if g.role_id == 2:
                orderlist = User_Purchase.query.filter_by(purchase_by_user=g.id).all()        
                return render_template('buyerorders.html', orders = orderlist, User = User, Product = Product)
            return redirect('/')
        return redirect('/')
        

order_history = Orderhistory.as_view('order_history')



class Buyprod(MethodView):
    def post(self, id):
        if g.username and g.role_id == 2:
            prod = Product.query.get(id)
            quantity = request.form['quantity']

            return render_template('buyprod.html', prod= prod, quantity = int(quantity))
        return redirect('/')

buyprod = Buyprod.as_view('buyprod')

class Placeorder(MethodView):
    def post(self, id):
        if g.username and g.role_id == 2:
            # interconnected objects
            buyer_obj = User.query.get(g.id)            
            seller_obj = User.query.get(Product.query.get(id).created_by_user)            
            prod_obj = Product.query.get(id)

            # order object data
            quantity = request.form['quantity']
            total_unit = int(quantity)

            #order details
            seller_name = seller_obj.first_name
            order_total = total_unit *  prod_obj.product_sell_price
            prodimg = prod_obj.product_img
            orderdate = date.today()

            if order_total > buyer_obj.balance:
                return 'you have insufficient balance'

            #adding to session
            a = User_Purchase(total_unit =  quantity, product_id = id, purchase_by_user = g.id, purchase_from_user= seller_obj.id )
            db.session.add(a)
            
            # updating seller and buyer balance and stock details
            buyer_obj.balance = buyer_obj.balance - order_total
            seller_obj.balance = seller_obj.balance + order_total
            prod_obj.stock_unit = prod_obj.stock_unit - total_unit            
            db.session.commit()

            return render_template('placeorder.html', quantity = quantity, seller = seller_name, prodname = prod_obj.product_name, prodimg = prodimg, totalprice =order_total, orderdate = orderdate)

        return redirect('/')

placeorder = Placeorder.as_view('placeorder')
        
class Editprofile(MethodView):
    def get(self):
        if g.username:
            user = User.query.get(g.id)
            return render_template('editprofile.html', user = user)
        return redirect('/')
    def post(self):
        if g.username:
            user = User.query.get(g.id)
            firstname = request.form['firstname']
            for i in firstname:
                if i.isdigit():
                    return 'please enter valid first name'
            lastname = request.form['lastname']
            for i in lastname:
                if i.isdigit():
                    return 'please enter validlastnae'
            mobile = request.form['mobile']
            if not mobile.isdigit():
                flash('please enter valid mobile number')   
                return Response('please enter valid number')
            if not len(mobile) == 10:
                return 'please enter 10 digit number'
            address = request.form['address']
            if len(address) > 200:
                return 'please '
            user.first_name = firstname    
            user.last_name = lastname                        
            user.mobile = mobile
            dob = request.form['dateofbirth'].split('-')
            year, month, day = dob
            user.date_of_birth = datetime(int(year), int(month), int(day))
            user.balance = request.form['balance']
            user.address = request.form['address']   
            db.session.commit()                 
            flash('profile updated successfully')
            return redirect('/')
        return redirect('/')

edit_profile = Editprofile.as_view('edit_profile')

class Changepassword(MethodView):
    def get(self):
        if g.username:
            return render_template('changepass.html')
        return redirect('/')

    def post(self):
        if g.username:
            user = User.query.get(g.id)
            oldpass = request.form['oldpassword']
            newpass = request.form['newpassword']
            if not user.password == oldpass:
                return 'incorrect oldpass'
            if oldpass == newpass:
                return r"old and new password can't be same"
            user.password = newpass
            db.session.commit()
            flash('password changed successfuly')
            return redirect('/')
        return redirect('/')

changepass = Changepassword.as_view('chang_pass')            

@app.before_request
def interseptor():
    g.username = None
    g.role_id =None
    g.id = None
    if 'user' in session:
        g.username = session['user']
        g.id = session['id']
        g.role_id = session['role_id']


@app.route('/logout')
def logout():
    session.pop('user', None)
    g.username = None
    g.id = None
    g.role_id = None
    return redirect('/')

@app.route('/deleteprod/<int:id>')
def deleteprod(id):
    if g.username:
        prod = Product.query.get(id)
        prod.is_deleted = False
        db.session.commit()
        flash(f'you have removed {prod.product_name}')
        return redirect('/viewproduct')
    return redirect('/')





app.add_url_rule('/signup/', methods=['GET','POST'], view_func=user_view)
app.add_url_rule('/', methods= ['GET','POST'], view_func=login_view)
app.add_url_rule('/login/', methods= ['GET','POST'], view_func=login_view)
app.add_url_rule('/home/', methods = ['GET', 'POST'], view_func=Homeview)
app.add_url_rule('/editproduct/<int:id>', methods=['GET','POST'], view_func=edit_view)
app.add_url_rule('/viewproduct/', methods = ['GET'], view_func =product_view)
app.add_url_rule('/addproduct/', methods = ['POST'], view_func =add_prod)
app.add_url_rule('/user/editprofile/', methods=['GET','POST'], view_func = edit_profile)
app.add_url_rule('/user/changepass/', methods=['GET', 'POST'], view_func = changepass)
app.add_url_rule('/buyproduct/<int:id>', methods=['POST'], view_func=buyprod)
app.add_url_rule('/placeorder/<int:id>', methods=['POST'], view_func=placeorder)
app.add_url_rule('/sellhistory', methods = ['GET'], view_func = sellhistory)
app.add_url_rule('/orders', methods = ['GET'], view_func = order_history)


if __name__ == "__main__":
    app.run(debug=True)
    


