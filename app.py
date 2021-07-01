#Authentication

from flask_bcrypt import Bcrypt
import os



#flask staff
from flask import Flask,render_template,request,url_for,session,redirect,flash,g,abort
from flask.globals import request
from flask_mysqldb import MySQL
import MySQLdb.cursors

#Login system



from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.fields.core import DateField, DecimalField
from wtforms.widgets.core import Select
app = Flask(__name__)

# Sending emails
import smtplib

#wtf info
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,TextField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, Email, InputRequired,EqualTo, Length

app = Flask(__name__)
# secret key
app.config["SECRET_KEY"]='lejshjsjbkc'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='admin'
app.config['MYSQL_PASSWORD']='lkk99@LKK99'
app.config['MYSQL_DB']='library'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql=MySQL(app)

#Authentication
bcrypt = Bcrypt()

@app.before_request
def before_request():
    g.email = None
    if 'email' in session:
        g.email = session['email']

@app.route('/authentication',methods=['POST','GET'])
def authenticate():
    form=loginform()
    if request.method == 'POST':
        uname = request.form['email']
        passwrd = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT email,password FROM accounts WHERE email=%s",[uname])
        user = cur.fetchone()
        temp = user[1]
        if len(user) > 0:
            session.pop('email',None)
            if (bcrypt.check_password_hash(temp,passwrd)) == True:
                session['email'] = request.form['email']
            return render_template('home.html',uname=uname)
        else:
            flash('Invalid Username or Password !!')
            return render_template('login.html',form=form)
    else:
        return render_template('login.html',form=form)



#classes

class Reminder(FlaskForm):
    message=StringField('message',validators=[DataRequired()])
    email=StringField('Email',validators=[DataRequired(),Length(min=3),Email()])
    submit = SubmitField('send')
    search = SubmitField('search')

class loginform(FlaskForm):
    email=StringField("Email",validators=[
        InputRequired('username is required'),Email()
        ])
    user_id=StringField("Admin_id",validators=[Length(max=8)])
    admin_id=StringField("Admin_id",validators=[Length(max=8)])
    password=PasswordField("password",
    validators=[InputRequired('password is required')])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username=StringField('username',validators=[DataRequired(),Length(min=3,max=20)])
    email=StringField('Email',validators=[DataRequired(),Length(min=3),Email()])
    password=PasswordField('password',validators=[Length(min=6),DataRequired()])
    confirm_password=PasswordField('confirm password',validators=[EqualTo('password')])
    submit = SubmitField('Sighn up')

class Book(FlaskForm):
    book_name=StringField('title',validators=[DataRequired()])
    book_id=StringField('id ',validators=[DataRequired()])
    price=StringField('Price', validators=[
        Length(min=4)
    ])
    book_description=StringField('description',validators=[DataRequired()])
    submit = SubmitField('ADD')

class Member(FlaskForm):
    member_name=StringField('Name',validators=[DataRequired()])
    member_id=StringField('ID ',validators=[DataRequired()])
    member_email=StringField('Email',validators=[
        DataRequired(),Length(min=3),Email()])
    member_phone=StringField("Phone",validators=[
        Length(min=8,max=8)
    ])
    Book_borrowed=StringField("Book Title",)
    Book_author=StringField("Author")
    Date_borrowed=DateField("Date")
    submit = SubmitField('ADD')

class Buy(FlaskForm):
    customer_name=StringField('Your Name',validators=[DataRequired()])
    p_id=StringField('product id ',validators=[DataRequired()])
    email=StringField('Email',validators=[
        DataRequired(),Length(min=3),Email()])
    phone=StringField("Phone no",validators=[
        Length(min=8,max=8)
    ])
    customer_id=StringField('Your Id',validators=[DataRequired(),Length(max=8)])
    items=StringField('No of Items',validators=[DataRequired()])
    method=StringField('cash on delivery, cash with order',[DataRequired()])
    submit = SubmitField('ADD TO PURCHASES')
    #Product Form
class Product(FlaskForm):
    p_name=StringField('Name',validators=[DataRequired()])
    p_id=StringField('id ',validators=[DataRequired()])
    price=StringField('Price', validators=[
        Length(min=4)
    ])
    p_description=StringField('description',validators=[DataRequired()])
    p_category=StringField('Category',validators=[Length(min=6)])
    submit = SubmitField('ADD PRODUCT')


    #Routes

@app.route('/home', methods=['GET','POST'])
def home():
    form=loginform()
    if g.email:
        return render_template('home.html')
    else:
        return render_template('accounts.html',form=form)
@app.route('/login', methods=['GET','POST'])
def login():
    form = loginform()
    if form.validate_on_submit():
        if request.method=='POST':
            #Record the user email into the filesystem/session 
            session["email"]=request.form.get("email")
            email=request.form['email']
            password=request.form['password']
            #check if the login details given are valid and exist
            query="SELECT email,password FROM accounts WHERE email=%s and password=%s"
            data=(email,password)
            cur = mysql.connection.cursor()
            cur.execute(query,data)
            details=cur.fetchone()
            mysql.connection.commit()
            if details:
                flash(f'Login successfully!',category='success')
                return redirect(url_for('home'))
            else:
                flash(f"sorry password and email did not match!",category='danger')
    return render_template('login.html',form=form)
@app.route('/adminlogin', methods=['GET','POST'])
def adminlogin():
    form = loginform()
    if form.validate_on_submit():
        if request.method=='POST':
            #Record the user email into the filesystem/session 
            session["email"]=request.form.get("email")
            email=request.form['email']
            id=request.form['admin_id']
            password=request.form['password']
            #check if the login details given are valid and exist
            query="SELECT email,password FROM accounts WHERE email=%s and password=%s"
            data=(email,password)
            cur = mysql.connection.cursor()
            cur.execute(query,data)
            mysql.connection.commit()
            details=cur.fetchone()
            if details:
                data=[id,]
                query="SELECT admin_id FROM admin WHERE admin_id=%s"
                cur.execute(query,data)
                mysql.connection.commit()
                details1=cur.fetchone()
                if details1:
                    flash(f'Login successfully!',category='success')
                    return render_template('manage.html')
            else:
                flash(f"sorry password and email did not match!",category='danger')
    return render_template('admin.html',form=form)

# The Logout route
@app.route('/logout',methods=['GET','POST'])
def logout():
    session["email"]=None
    if session["email"]==None:
        return redirect(url_for("login"))
    else:
        return redirect(url_for('home'))

@app.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.email and form.username and form.password and form.confirm_password and request.method == 'POST':
            email=request.form['email']
            username=request.form['username']
            p=request.form['password']
            password=generate_password_hash(request.form['password'])
            data=(username,email,password,p)
            query="INSERT INTO accounts(username,email,password1,password) VALUES (%s,%s,%s,%s)"
            cur = mysql.connection.cursor()
            cur.execute(query,data)
            mysql.connection.commit()
            cur.close()
            flash(f'account created successfully! for {form.username.data}',category='success')
            return redirect('login')
        else:
            flash(f' Invalid details!',category='danger')
    return render_template('register.html',form=form)


@app.route('/',methods=['GET','POST'])
def accounts():
    if request.method=='POST':
        #If the user has no record in the page then the user should login first
        if not session.get("email"):
           return redirect(url_for("login"))
        else:
            session["loggedin"]="loggedin"
    return render_template('accounts.html')

#Add new books into te library
@app.route('/new',methods=['POST','GET'])
def new_book():
    if request.method=='POST' :
        
        #,request.form['book_description'],request.form['author'],request.form['book_category'],request.form['status']]
        price="'${}'".format(request.form['price'])
        data=[request.form['book_id'],request.form['book_name'],request.form['book_description'],request.form['author'],request.form['book_category'],request.form['status'],price]
        query="INSERT INTO books(book_id,book_name,book_descrption,author,book_category,status,price) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            #adding into auto incremented column tables needs the added columns specified
        cur=mysql.connection.cursor()
        cur.execute(query,data)
        mysql.connection.commit()
        cur.close()
        flash(f'Successfully added')
        return redirect(url_for("show_books"))


#Displayng the books to admin
@app.route('/books',methods=['GET','POST'])
def show_books():
    query ="SELECT * FROM books order by book_id"
    cur=mysql.connection.cursor()
    cur.execute(query)
    books=cur.fetchall()
    mysql.connection.commit()
    cur.close()
    book=books[0]
    price='${}'.format(book['price'])
    return render_template('manageBooks.html',form=books,price=price)

#Display books to members
@app.route('/u_books',methods=['GET','POST'])
def show_books_users():
    status="Available"
    lent="Lent"
    query ="SELECT * FROM books order by book_id"
    cur=mysql.connection.cursor()
    cur.execute(query)
    books=cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return render_template('book.html',form=books,status=status,lent=lent)
#Display the members
@app.route('/Users',methods=['GET','POST'])
def Manage_Members():
        query = "SELECT* FROM members"
        cur=mysql.connection.cursor()
        cur.execute(query)
        members=cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('managemembers.html',form=members)
#Add members
@app.route('/new_user',methods=['POST','GET'])
def new_member():
    if request.method=='POST':
        data=(request.form['member_id'],request.form['member_name'],request.form['member_phone'],request.form['member_email'])
        query="INSERT INTO Members(member_id,member_name,member_phone,member_email)VALUES(%s,%s,%s,%s)"
        cur=mysql.connection.cursor()
        cur.execute(query,data)
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("Manage_Members"))

#Through mail remind the user about the due date to return a lent book
@app.route('/reminder',methods=['POST','GET'])

def reminder():
    form=Reminder()
    email=request.form.get("email")
    if request.method=="POST":
        admin="lennoxkk7@gmail.com"
        #check if the accounts exists
        query="SELECT email FROM accounts WHERE email='lennoxkk7@gmail.com'"
        #lennoxkk7@gmail.com"
        cur=mysql.connection.cursor()
        cur.execute(query)
        mysql.connection.commit()
        ready=cur.fetchone()
        if ready:
            message=request.form["message"]
            server=smtplib.SMTP("smtp.gmail.com",587)
            server.starttls()
            server.login("lennoxkk7@gmail.com","LennoxEKK99@")
            server.sendmail("lennoxkk7@gmail.com",admin,message)
            flash(f'sent',category="success")
        else:
            flash(f"Invalid mail!")
    return render_template("reminder.html",form=form)
#update book details
@app.route('/update',methods=['GET','POST'])
def update_book():
    cur=mysql.connection.cursor()
    id=["'{}'".format(request.form['book_id']),]
    cur.execute("SELECT * FROM books WHERE book_id=%s",id)
    book=cur.fetchall()
    if request.method=="POST" and book:
        cur=mysql.connection.cursor()
        id="'{}'".format(request.form['book_id'])
        #Update the book_name
        book_name=[request.form['book_name'],]
        cur.execute("update books set book_name=%s WHERE book_id ="+id,book_name)
        mysql.connection.commit()

        #Update the author
        author=[request.form['author'],]
        cur.execute("update books set author=%s WHERE book_id ="+id,author)
        mysql.connection.commit()

        #update the description
        description=[request.form['book_description'],]
        cur.execute("update books set book_descrption=%s  WHERE book_id ="+id,description)
        mysql.connection.commit()

        #update book status 
        status=[request.form['status'],]
        cur.execute("update books set status=%s WHERE book_id ="+id,status)
        mysql.connection.commit()

        #Update book price
        price=[request.form['price'],]
        cur.execute("update books set price=%s WHERE book_id ="+id,price)
        mysql.connection.commit()
        cur.close()
        flash(f'Successfully updated ',category="success")
        return redirect(url_for("show_books"))
    else:
        flash(f'Object not found! Check the id and corrrect it',category="success")
        return redirect(url_for("show_books"))




#UPDATE PRODUCT DETAILS
@app.route('/update_product',methods=['GET','POST'])
def update_product():
    cur=mysql.connection.cursor()
    data=[request.form['product_id'],]
    id="'{}'".format(data[0])
    cur.execute("select * from products where roduct_id=%s",data)
    product=cur.fetchall()
    if request.method=="POST" and product:
        #Update the member_name
        product_name=[request.form['product_name'],]
        cur.execute("update products set product_name=%s WHERE roduct_id="+id,product_name)
        mysql.connection.commit()

        #Update the member_phone
        product_description=[request.form['product_description'],]
        cur.execute("update products set product_description=%s WHERE roduct_id="+id,product_description)
        mysql.connection.commit()

        #update the description
        product_category=[request.form['category'],]
        cur.execute("update products set product_category=%s  WHERE roduct_id ="+id,product_category)
        mysql.connection.commit()

        #UPDATE PRODUCT PRICE
        product_price=[request.form['price'],]
        cur.execute("update products set product_price=%s  WHERE roduct_id ="+id,product_price)
        mysql.connection.commit()

        cur.close()
        flash(f'Successfully updated ',category="success")
        return redirect(url_for("display_products"))
    else:
        flash(f'Object not found! Check the id and corrrect it',category="success")
        return redirect(url_for("display_products"))



#Update member details
#update book details
@app.route('/update_member',methods=['GET','POST'])
def update_member():
    cur=mysql.connection.cursor()
    data=[request.form['member_id'],]
    id="'{}'".format(data[0])
    cur.execute("SELECT* FROM members WHERE member_id=%s",data)
    member=cur.fetchall()
    if request.method=="POST" and member:
        cur=mysql.connection.cursor()
        data=[request.form['member_id'],]
        id="'{}'".format(data[0])
        #Update the member_name
        member_name=[request.form['member_name'],]
        cur.execute("update members set member_name=%s WHERE member_id ="+id,member_name)
        mysql.connection.commit()

        #Update the member_phone
        member_phone=[request.form['member_phone'],]
        cur.execute("update members set member_phone=%s WHERE member_id ="+id,member_phone)
        mysql.connection.commit()

        #update the description
        member_email=[request.form['email'],]
        cur.execute("update members set member_email=%s  WHERE member_id ="+id,member_email)
        mysql.connection.commit()

        cur.close()
        flash(f'Successfully updated ',category="success")
        return redirect(url_for("Manage_Members"))
    else:
        flash(f'Object not found! Check the id and corrrect it',category="success")
        return redirect(url_for("Manage_Members"))
#Update book issues
@app.route('/update_issues',methods=['GET','POST'])
def update_issues():
    cur=mysql.connection.cursor()
    data=[request.form['issue_id'],]
    cur.execute("SELECT* FROM issues WHERE issue_id=%s",data)
    issue=cur.fetchall()
    if request.method=="POST" and issue:
        cur=mysql.connection.cursor()
        data=[request.form['issue_id'],]
        id="'{}'".format(data[0])
        #Update the date borrowed 
        date_borrowed=[request.form['date_borrowed'],]
        cur.execute("update issues set date_lent=%s WHERE issue_id ="+id,date_borrowed)
        mysql.connection.commit()
        # update date returned
        date_returned=[request.form['date_returned'],]
        cur.execute("update issues set date_returned=%s WHERE issue_id ="+id,date_returned)
        mysql.connection.commit()
        #Update the member_phone

        #update the description
        penalty=[request.form['penalty'],]
        cur.execute("update issues set penalty=%s  WHERE issue_id ="+id,penalty)
        mysql.connection.commit()

        cur.close()
        flash(f'Successfully updated ',category="success")
        return redirect(url_for("Record_issue"))
    else:
        flash(f'Object not found! Check the id and corrrect it',category="success")
        return redirect(url_for("Record_issue"))

#Delete a table for books
@app.route('/delete',methods=['GET','POST'])
def delete_table():
    if request.method=='POST':
        query="DROP TABLE IF EXISTS %s"
        data=[request.form['table_name'],]
        print(data)
        if data:
            print(data)
            cur=mysql.connection.cursor()
            cur.execute(query,data)
            mysql.connection.commit()
            cur.close()
            return redirect(url_for("show_books"))
        else:
            flash('no name given',category="danger")
            return redirect(url_for("show_books"))
#Delete table for members
@app.route('/delete_m',methods=['GET','POST'])
def delete_member_table():
    if request.method=='POST':
        query="DROP TABLE IF EXISTS %s"
        data=[request.form['table_name'],]
        if data:
            cur=mysql.connection.cursor()
            cur.execute(query,data)
            mysql.connection.commit()
            cur.close()
            return redirect(url_for("show_members"))
        else:
            flash('no name given',category="danger")
            return redirect(url_for("show_members"))
@app.route('/delete_m',methods=['GET','POST'])
def show_members():
    return render_template('members.html')
#Delete only a row of the books table
@app.route('/book',methods=['GET','POST'])
def delete_row():
    if request.method=="POST":
        cur=mysql.connection.cursor()
        data=[request.form['book_id'],]
        cur.execute("SELECT* FROM books WHERE book_id=%s",data)
        book=cur.fetchall()
        mysql.connection.commit()
        if book:
            data=[request.form['book_id'],]
            query="DELETE FROM books WHERE book_id=%s"
            cur.execute(query,data)
            mysql.connection.commit()
            flash(f'deleted',category="success")
            cur.close()
            return redirect(url_for('show_books'))
        else:
            flash(f'Cannot trace the object check the id if is correct',category="danger")
            return redirect(url_for('show_books'))



#DELETE PRODUCT 
@app.route('/pruduc_delete',methods=['GET','POST'])
def delete_product():
    if request.method=="POST":
        cur=mysql.connection.cursor()
        data=[request.form['product_id'],]
        cur.execute("SELECT* FROM products WHERE roduct_id=%s",data)
        book=cur.fetchall()
        mysql.connection.commit()
        if book:
            data=[request.form['product_id'],]
            query="DELETE FROM products WHERE roduct_id=%s"
            cur.execute(query,data)
            mysql.connection.commit()
            flash(f'deleted',category="success")
            cur.close()
            return redirect(url_for('display_products'))
        else:
            flash(f'Cannot trace the object check the id if is correct',category="danger")
            return redirect(url_for('display_products'))

#Delete user row
@app.route('/remove',methods=['GET','POST'])
def delete_member():
    if request.method=="POST":
        cur=mysql.connection.cursor()
        data=[request.form['member_id'],]
        cur.execute("SELECT* FROM members WHERE member_id=%s",data)
        member=cur.fetchall()
        mysql.connection.commit()
        if member:
            cur.execute("select * from issues where member_id=%s ",data)
            mysql.connection.commit()
            issue=cur.fetchone()
            if issue:
                flash("The member has a book! cant delete untill the book is returned",category="success")
                return redirect(url_for('Issues'))
            query="DELETE FROM members WHERE member_id=%s"
            cur.execute(query,data)
            flash(f'deleted',category="success")
            cur.close()
            return redirect(url_for('show_members'))
        else:
            flash(f'Cannot trace the object check the id if is correct',category="danger")
            return redirect(url_for('Manage_Members'))
#Delete user row
@app.route('/remove_issue',methods=['GET','POST'])
def delete_issue():
    if request.method=="POST":
        cur=mysql.connection.cursor()
        data=[request.form['issue_id'],]
        m=[request.form['book_id'],]
        cur.execute("SELECT book_id FROM ISSUES WHERE issue_id=%s",data)
        mysql.connection.commit()
        member=cur.fetchall()

        if member:
            query="DELETE FROM issues WHERE issue_id=%s"
            cur.execute("UPDATE BOOKS SET status='1' WHERE book_id=%s",m)
            cur.execute(query,data)
            mysql.connection.commit()

            flash(f'Removed',category="success")
            cur.close()
            return redirect(url_for('Issues'))
        else:
            flash(f'Cannot trace the object check the id if is correct',category="danger")
            return redirect(url_for('Manage_Members'))
    
@app.route('/search',methods=["GET","POST"])
def page():
    if request.method=='POST':
        message="'%{}%'".format(request.form['search2'])
        query="SELECT* FROM books WHERE book_name LIKE "+message
        query1="SELECT* FROM products WHERE product_name LIKE "+message
        cur=mysql.connection.cursor()
        cur.execute(query)
        mysql.connection.commit()
        result1=cur.fetchall()
        cur.close()
        cur=mysql.connection.cursor()
        cur.execute(query1)
        mysql.connection.commit()
        result2=cur.fetchall()
        if result1 or result2:
            return render_template('search.html',result=result1,result2=result2)
        else:
            flash(f'Sorry nothing related to your search was found! check your spelling!',category='danger')
            return redirect(url_for('home'))
#display products
@app.route('/products',methods=["GET","POST"])
def display_products():
    cur=mysql.connection.cursor()
    cur.execute("SELECT* FROM products INNER JOIN suplliers")
    mysql.connection.commit()
    products=cur.fetchall()
    if products:
        return render_template('products.html',form=products)
    else:
        flash(f'No products yet',category="danger")
        return render_template('products.html',form=products)

#Shopping display of books
@app.route('/p_description',methods=['POST','GET'])
def p_description():
    
        form=Member()
        book=Book()
        query="select product_description,product_name, roduct_id,product_price from products WHERE roduct_id='P1'"
        cur=mysql.connection.cursor()
        cur.execute(query)
        mysql.connection.commit()
        product=cur.fetchall()
        product_details=product[0]
        name= product_details['product_name']
        d= product_details['product_description']
        p_id=product_details['roduct_id']
        p='{}{}'.format("$",product_details['product_price'])
        return  render_template("product.html",product=d,id=p_id,price=p,name=name,form=form,book=book)
#Add a book to display
@app.route('/add_to_display',methods=['POST','GET'])
def add_to_display():
    form=Book()
    if form.validate_on_submit():
        if request.method=='POST':
            data=(request.form['book_id'],request.form['book_name'],request.form['book_description'])
            query="INSERT INTO books(book_id,book_name,book_descrption)VALUES(%s,%s,%s)"
            #adding into auto incremented column tables needs the added columns specified
            cur=mysql.connection.cursor()
            cur.execute(query,data)
            mysql.connection.commit()
            cur.close()
            return redirect(url_for("show_books"))
    return render_template('admin.html',form=form)

#New product
@app.route('/add_product',methods=['POST','GET'])
def new_produc():
        if request.method=='POST':
            data=(request.form['product_id'],request.form['product_name'],request.form['product_description'],request.form['price'],request.form['product_category'])
            id=[request.form['product_id'],]
            query="INSERT INTO products(roduct_id,product_name,product_description,product_price,product_category)VALUES(%s,%s,%s,%s,%s)"
            #adding into auto incremented column tables needs the added columns specified
            cur=mysql.connection.cursor()
            cur.execute("SELECT *from products WHERE roduct_id=%s",id)
            mysql.connection.commit()
            exist=cur.fetchall()
            if exist:
                flash(f'Product already exists!',category="danger")
                return redirect(url_for("display_products"))
            else:
                cur.execute(query,data)
                mysql.connection.commit()
                cur.close()
                
                flash(f'product added successfully!' ,category='success')
                return redirect(url_for("display_products"))
        else:
            flash(f'Failed to add product!',category='danger')
            return redirect(url_for("display_products"))
@app.route('/reserve',methods=['GET','POST'])
def reserve():
    form=Book()
    form2=loginform()
    if g.email:
        day=""
        month=""
        if request.method=='POST':
            j=0
            data=request.form['date_lent']
            for i in data:
                if j==5 or j==6:
                    month+=i
                if j==8 or j==9:
                    day+=i
                j=j+1
            year=data[0:4]
            b=int(day)+14
            if month=="04" or month=="06" or month=="09" or month=="11":
                b=b%30
                if b>30:
                    month="0"+str(int(month)+1)
                day=str(b)
            if month=="07" or month=="08" or month=="10" or month=="12" or month=="03" or month=="01" or month=="05":
                b=b%31
                if b>31:
                    month="0"+str(int(month)+1)
                day=str(b)
            if month=="02":
                if int(year) % 4 ==0:
                    if int(year) % 100 ==0:
                        if int(year) % 400 ==0:
                            
                            if b>29:
                                month="0"+str(int(month)+1)
                            b=b%29
                            day=str(b)
                        else:
                           
                            if b>28:
                                month="0"+str(int(month)+1)
                            b=b%28
                            day=str(b)
                    else:
                        if b>29:
                            month="0"+str(int(month)+1)
                        b=b%29
                        day=str(b)
                else:
                    if b>28:
                        month="0"+str(int(month)+1)
                    b=b%28
                    day=str(b)

            date_returned=year+"-"+month+"-"+day
            data=[request.form['date_lent'],date_returned,
            0,"A12",request.form['book_id'],request.form['member_id']]
            cur=mysql.connection.cursor()
            query="select status from books where book_id=%s"
            id=[request.form['book_id'],]
            m=[request.form['member_id'],]
            cur.execute(query,id)
            mysql.connection.commit()
            book=cur.fetchall()
            h=book[0]
            k=h['status']
            if k==False:
                    #Go and insert the dates 
                cur.execute("SELECT * FROM members where member_id = %s",m)
                mysql.connection.commit()
                member=cur.fetchone()
                if member:
                
                    cur.execute("INSERT INTO issues(date_lent,date_returned,penalty,staff_id,book_id,member_id) VALUES (%s,%s,%s,%s,%s,%s)",data)
                    cur.execute("UPDATE books SET status='1' WHERE book_id=%s",id)
                    mysql.connection.commit()

                    return redirect(url_for('Issues'))
                else:
                    m=[request.form['member_id'],request.form['member_name'],request.form['phone'],]
                    cur.execute("INSERT INTO members(member_id,member_name,member_phone) VALUES (%s,%s,%s)",m)
                    cur.execute("INSERT INTO issues(date_lent,date_returned,penalty,staff_id,book_id,member_id) VALUES (%s,%s,%s,%s,%s,%s)",data)
                    cur.execute("UPDATE books SET status='1' WHERE book_id=%s",id)
                    mysql.connection.commit()
                    return redirect(url_for('Member_status'))
            elif k==True:
                flash(f"The book has already been lent! choose another one!",category="success")
                return redirect(url_for('show_books'))
        else:
            flash(f'Book is not availabe! choose another one here',category="success")
            return redirect(url_for('show_books'))
    else:
        flash(f'Please login or register before proceeding!',category="danger")
        return render_template('accounts.html',form=form2)

   # return render_template("Reserve.html",form=form)

@app.route('/popular',methods=["GET","POST"])
def popular_books():
    return render_template('popular.html')

#Book categories @Novels
@app.route('/novels',methods=['GET','POST'])
def novels():
    query="SELECT* FROM books WHERE book_category LIKE '%novel%'"
    cur=mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    novel=cur.fetchall()
    if novel:
        return render_template('book.html',form=novel)
    else:
        flash('No books under that category yet',category="danger!")
        return redirect(url_for('show_books_users'))

@app.route('/journals' , methods=['GET','POST'])
def journals():
    query="SELECT* FROM books WHERE book_category LIKE '%journal%'"
    cur=mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    journal=cur.fetchall()
    if journal:
        return render_template('book.html',form=journal)
    else:
        flash('No books under that category yet',category="danger!")
        return redirect(url_for('show_books_users'))

#Book categories poems

@app.route('/Poetic' , methods=['GET','POST'])
def poems():
    query="SELECT* FROM books WHERE book_category LIKE '%poet%'"
    cur=mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    poem=cur.fetchall()
    if poem:
        return render_template('book.html',form=poem)
    else:
        flash('No books under that category yet',category="danger!")
        return redirect(url_for('show_books_users'))
@app.route('/magazines' , methods=['GET','POST'])
def magazines():
    query="SELECT* FROM WHERE book_category LIKE '%magazine%'"
    cur=mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    poem=cur.fetchall()
    if poem:
        return render_template('book.html',form=poem)
    else:
        flash('No books under that category yet',category="danger!")
        return redirect(url_for('show_books_users'))
@app.route('/issue',methods=['GET','POST'])
def Issues():
    query="SELECT issues.book_id,issues.issue_id,issues.member_id,admin.name,members.member_name,members.member_phone,issues.penalty,issues.date_lent,issues.date_returned,books.book_name,books.author,books.book_id FROM issues INNER JOIN books ON issues.book_id=books.book_id INNER JOIN admin ON issues.staff_id=admin.admin_id INNER JOIN members ON members.member_id=issues.member_id"
    cur=mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    issue=cur.fetchall()
    cur.close()
    if issue:
        return render_template('all_users.html',form=issue)
    else:
        flash(f'No members Yet!',category="danger")
        return redirect(url_for('new_member'))

@app.route('/record',methods=['GET','POST'])
def Record_issue():
    if request.method=='POST':
        data=[request.form['date_lent'],request.form['date_returned'],
        request.form['penalty'],request.form['staff_id'],request.form['book_id'],request.form['member_id']]
        cur=mysql.connection.cursor()
        query="select status from books where book_id=%s"
        id=[request.form['book_id'],]
        m=[request.form['member_id'],]
        cur.execute(query,id)
        mysql.connection.commit()
        book=cur.fetchone()
        k=book['status']
        if k==False:
                    #Go and insert the dates 
            cur.execute("SELECT * FROM members where member_id = %s",m)
            mysql.connection.commit()
            member=cur.fetchone()
            if member:
                
                cur.execute("INSERT INTO issues(date_lent,date_returned,penalty,staff_id,book_id,member_id) VALUES (%s,%s,%s,%s,%s,%s)",data)
                cur.execute("UPDATE books SET status='0' WHERE book_id=%s",id)
                mysql.connection.commit()

                return redirect(url_for('Issues'))
            else:
                 m=[request.form['member_id'],request.form['member_name'],request.form['phone'],]
                 cur.execute("INSERT INTO members(member_id,member_name,member_phone) VALUES (%s,%s,%s)",m)
                 cur.execute("INSERT INTO issues(date_lent,date_returned,penalty,staff_id,book_id,member_id) VALUES (%s,%s,%s,%s,%s,%s)",data)
                 cur.execute("UPDATE books SET status='0' WHERE book_id=%s",id)
                 mysql.connection.commit()
                 return redirect(url_for('Issues'))
        elif k==True:
            flash(f"The book has already been lent! choose another one!",category="success")
            return redirect(url_for('show_books'))
        else:
            flash(f'Book is not availabe! choose another one here',category="success")
            return redirect(url_for('show_books'))

#books status
@app.route('/book_status',methods=['GET','POST'])
def Member_status():
    query="SELECT issues.book_id,books.status,issues.member_id,members.member_name,issues.penalty,issues.date_lent,issues.date_returned,books.book_name,books.author,books.book_id FROM issues INNER JOIN books ON issues.book_id=books.book_id INNER JOIN members ON issues.member_id=members.member_id"
    cur=mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    issue=cur.fetchall()
    cur.close()
    if issue:
        return render_template('member_view.html',form=issue)
    else:
        flash(f'No members Yet!',category="danger")
        return redirect(url_for('new_member'))

@app.route('/test' , methods=['GET','POST'])
def test():
    form=Reminder()
    return render_template('contact.html',form=form)

#Buy goods
@app.route('/buy',methods=['GET','POST'])
def buy_product():
    form=Buy()
    form1=loginform()
    if g.email:
            if form.validate_on_submit:
                if request.method=='POST':
                    data0=[request.form['phone'],]
                    data1=[request.form['customer_id'],request.form['p_id'],request.form['method'],request.form['items']]
                    data2=[request.form['customer_name'],
                    request.form['phone'],request.form['email'],request.form['customer_id']]
                    query1="INSERT INTO transactions(customer_id,roduct_id,method_of_payment,items,date_done,admin_id) VALUES(%s,%s,%s,%s,'2021-07-02','A12')"
                    query2="INSERT INTO customers(customer_name,phone,email,customer_id) VALUES(%s,%s,%s,%s)"
                    query3="SELECT* FROM products WHERE roduct_id=%s"
                    cur=mysql.connection.cursor()
                    cur.execute(query2,data2)
                    cur.execute(query1,data1)
                    cur.execute(query3,data0)
                    mysql.connection.commit()
                    id=cur.fetchone()
                    if id:
                        cur.execute(query1,data1)
                        mysql.connection.commit()
                    else:
                        flash(f"Incorect id!",category="danger")
                        return redirect(url_for('p_description'))
            return render_template('purchase.html',form=form)
    else:
        return render_template('accounts.html',form=form)
@app.route('/contact',methods=['POST','GET'])
#CONTACT PAGE
def contact():
    form=loginform()
    if g.email:
        return render_template("contact.html")
    else:
        return render_template('accounts.html',form=form)
    


#admin management site
@app.route('/admin',methods=['POST','GET'])
def manage():
    return render_template("manage.html")
#purchases 
@app.route('/details',methods=['POST','GET'])
def purchase():
    form=Buy()
    return render_template('add_member.html',form=form)
@app.route('/about',methods=['GET','POST'])
def about():
    return render_template('about.html')
#

#Error handling
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)