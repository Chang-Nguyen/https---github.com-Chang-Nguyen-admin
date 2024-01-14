import secrets
import os
from cloudinary.uploader import upload, destroy
import cloudinary
from application import ALLOWED_EXTENSIONS, db,UPLOAD_FOLDER
from application import app, mongo
from flask import Flask, jsonify, render_template, session, url_for, request, redirect, flash, send_from_directory
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
import bcrypt
from bson import ObjectId


CLOUD_NAME='dc7qea6ql'
API_KEY='586546361886479'
API_SECRET='V-aVq1lFIXIUDz1SGoz-Eq5sf94'

# cloudinary.config(cloud_name = CLOUD_NAME, api_key=API_KEY, 
#     api_secret=API_SECRET)

#table
nav = db.nav
category = db.category
book = db.book
product = db.product
blog = db.blog
admin = db.admin
reviews = db.reviews
user = db.user
order = db.order

def dockerMongoDB():
    pw = "test123"
    hashed = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
    admin.insert_one({
        "name": "admin123",
        "email": "admin123@gmail.com",
        "password": hashed
    })
    return admin

admin = dockerMongoDB()

@app.route("/", methods=["POST", "GET"])
def login():
    message = 'Nhập tài khoản để đăng nhập!!'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        #check if email exists in database
        email_found = admin.find_one({"email": email})
        if email == '':
            message = 'Email không được bỏ trống!!'
            return render_template('login.html', message=message)  
        if email_found:
            
            passwordcheck = email_found['password']
            #encode the password and check if it matches
            if password == '':
                message = 'Mật khẩu không được bỏ trống!!'
                return render_template('login.html', message=message)
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                
                return redirect('body')
            else:
                if "email" in session:
                    return redirect("body")
                message = 'Mật khẩu không chính xác!!'
                return render_template('login.html', message=message)
        else:
            message = 'Email của bạn đang sai!!'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

@app.route('/body')
def logged_in():
        return render_template('statistical.html')

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('index.html')
    
@app.route("/product", methods=('GET', 'POST'))
def get_products():
    if request.method == 'GET':
        allData = db['product'].find()
        dataJson = []
        for data in allData:
            id = data['_id']
            product_name = data['product_name']
            product_price = data['product_price']
            product_info = data['product_info']
            product_type = data['product_type']
            product_img1 = data['product_img1']
            dataDict = {
                'id': str(id),
                'product_name': product_name,
                'product_price': product_price,
                'product_info': product_info,
                'product_type': product_type,
                'product_img1': product_img1
            }
            dataJson.append(dataDict)
        print(dataJson)
        return jsonify(dataJson)

@app.route("/product/<id>/", methods=['GET', 'POST'])
def get_product(id):
    if request.method == 'GET':
        oneData = db['product'].find_one({"_id": ObjectId(id)})
        if oneData:
            dataDict = {
                'id': str(oneData['_id']),
                'product_name': oneData['product_name'],
                'product_price': oneData['product_price'],
                'product_info': oneData['product_info'],
                'product_type': oneData['product_type'],
                'product_img1': oneData['product_img1']
            }
            return jsonify(dataDict)
        else:
            return jsonify({'message': 'Product not found'}), 404


@app.route("/add_product", methods=('GET', 'POST'))
def upload_file():
    app.logger.info('in upload route')

    cloudinary.config(cloud_name = CLOUD_NAME, api_key=API_KEY, 
        api_secret=API_SECRET)
    upload_result = None
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        product_price = request.form.get('product_price')
        product_info = request.form.get('product_info')
        product_type = request.form.get('product_type')
        file_to_upload = request.files['product_img1']
        app.logger.info('%s file_to_upload', file_to_upload)
        if file_to_upload:
          upload_result = cloudinary.uploader.upload(file_to_upload)
          app.logger.info(upload_result)
        url_img = upload_result
        product.insert_one({'product_name': product_name, 'product_price': product_price, 'product_info': product_info, 'product_type': product_type, 'product_img1': url_img})
    all_product = product.find() 
    return render_template('add_product.html', product=all_product)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post("/<id>/deleteProduct/")
def delete_product(id):  # delete function by targeting a todo document by its own id
    product.delete_one({"_id": ObjectId(id)})  # deleting the selected todo document by its converted id
    return redirect('/add_product')

# get category
@app.route("/news", methods=('GET', 'POST'))
@app.route("/order", methods=('GET', 'POST'))
def get_news():
    if request.method == 'GET':
        allData = db['category'].find()
        dataJson = []
        for data in allData:
            id = data['_id']
            category_name = data['category_name']
            dataDict = {
                'id': str(id),
                'category_name': category_name,
            }
            dataJson.append(dataDict)
        print(dataJson)
        return jsonify(dataJson)

#category

@app.route("/add_category", methods=('GET', 'POST'))
def get_category():
    if request.method == "POST": 
        category_name = request.form.get('category_name')
        category.insert_one({'category_name': category_name})
        return redirect('/add_category') 
    all_category = category.find() 
    return render_template('add_category.html', category=all_category) 


@app.post("/<id>/deleteCategory/")
def delete_category(id):  # delete function by targeting a todo document by its own id
    category.delete_one({"_id": ObjectId(id)})  # deleting the selected todo document by its converted id
    return redirect('/add_category')

#book
@app.route("/add_book", methods=('GET', 'POST'))
def add_book():
    if request.method == "POST": 
        name = request.form.get('name')
        phone = request.form.get('phone')
        date = request.form.get('date')
        time = request.form.get('time')
        facility = request.form.get('facility')
        adults = request.form.get('adults')
        children = request.form.get('children')
        note = request.form.get('note')
        book.insert_one({'name': name, 'phone': phone, 'date': date, 'time': time, 'facility': facility, 'adults': adults, 'children': children, 'note': note})
        return redirect('/add_book') 
    all_book = book.find() 
    return render_template('add_book.html', book=all_book)




@app.post("/<id>/deleteBook/")
def delete_book(id):  # delete function by targeting a todo document by its own id
    book.delete_one({"_id": ObjectId(id)})  # deleting the selected todo document by its converted id
    return redirect('/add_book')



#Nav
@app.route("/add_nav", methods=('GET', 'POST'))
def index_nav():
    if request.method == "POST": 
        nav_content = request.form.get('nav_content')
        nav.insert_one({'nav_content': nav_content})
        return redirect('/add_nav') 
    all_nav = nav.find() 
    return render_template('add_nav.html', nav=all_nav) 


@app.post("/<id>/deleteNav/")
def delete_nav(id):  # delete function by targeting a todo document by its own id
    nav.delete_one({"_id": ObjectId(id)})  # deleting the selected todo document by its converted id
    return redirect('/add_nav')

@app.route("/add_blog", methods=('GET', 'POST'))
def upload_blog():
    app.logger.info('in upload route')

    cloudinary.config(cloud_name=CLOUD_NAME, api_key=API_KEY, api_secret=API_SECRET)
    upload_result = None
    all_blog = ["blog"]  

    if request.method == 'POST':
        blog_name = request.form.get('blog_name')
        blog_info = request.form.get('blog_info')
        file_to_upload = request.files['blog_img']
        app.logger.info('%s file_to_upload', file_to_upload)

        if file_to_upload and allowed_files(file_to_upload.filename):
            upload_result = cloudinary.uploader.upload(file_to_upload)
            app.logger.info(upload_result)
            url_img = upload_result
            blog.insert_one({'blog_name': blog_name, 'blog_info': blog_info, 'blog_img': url_img})

        # Move the assignment inside the if block
        all_blog = blog.find()

    return render_template('add_blog.html', blog=all_blog)


def allowed_files(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/blog", methods=('GET', 'POST'))
def get_blog():
    if request.method == 'GET':
        allData = db['blog'].find()
        dataJson = []
        for data in allData:
            id = data['_id']
            blog_name = data['blog_name']
            blog_info = data['blog_info']
            blog_img = data['blog_img']
            dataDict = {
                'id': str(id),
                'blog_name': blog_name,
                'blog_info': blog_info,
                'blog_img': blog_img
            }
            dataJson.append(dataDict)
        print(dataJson)
        return jsonify(dataJson)
    
@app.route("/blog/<id>/", methods=['GET', 'POST'])
def get_blogs(id):
    if request.method == 'GET':
        oneData = db['blog'].find_one({"_id": ObjectId(id)})
        if oneData:
            dataDict = {
                'id': str(oneData['_id']),
                'blog_name': oneData['blog_name'],
                'blog_info': oneData['blog_info'],
                'blog_img': oneData['blog_img']
            }
            return jsonify(dataDict)
        else:
            return jsonify({'message': 'Product not found'}), 404
    
@app.post("/<id>/deleteBlog/")
def delete_blog(id):  # delete function by targeting a todo document by its own id
    nav.delete_one({"_id": ObjectId(id)})  # deleting the selected todo document by its converted id
    return redirect('/add_blog')

@app.route("/add_reviews", methods=('GET', 'POST'))
def add_reviews():
    if request.method == "POST": 
        name = request.form.get('name')
        star = request.form.get('star')
        note = request.form.get('note')
        reviews.insert_one({'name': name, 'star': star, 'note': note})
        return redirect('/add_reviews') 
    all_reviews = reviews.find() 
    return render_template('add_reviews.html', reviews=all_reviews)




@app.post("/<id>/deleteReviews/")
def delete_reviews(id):  # delete function by targeting a todo document by its own id
    reviews.delete_one({"_id": ObjectId(id)})  # deleting the selected todo document by its converted id
    return redirect('/add_reviews')

# user
@app.route("/add_user", methods=('GET', 'POST'))
def add_user():
    if request.method == "POST":
        name = request.form.get('name')
        phone = request.form.get('phone')
        city = request.form.get('city')
        district = request.form.get('district')
        commune = request.form.get('commune')
        address = request.form.get('address')
        method_payment = request.form.get('method-payment')

        user.insert_one({'name': name, 'phone': phone, 
        'city': city, 'district': district, 'commune': commune, 
        'address': address, 'method_payment': method_payment })

        return redirect('/add_user')
    all_user = user.find() 
    return render_template('add_user.html', user=all_user)

@app.post("/<id>/deleteUser/")
def delete_user(id):  # delete function by targeting a todo document by its own id
    user.delete_one({"_id": ObjectId(id)})  # deleting the selected todo document by its converted id
    return redirect('/add_user')

@app.route("/add_order", methods=['GET', 'POST'])
@app.route("/add_user", methods=('GET', 'POST'))
def add_order():
    if request.method == "POST":
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        method_payment = request.form.get('method-payment')
        name_product = request.form.get('name_product')
        quantity = request.form.get('quantity')
        total = request.form.get('total')

        order.insert_one({'name': name, 'phone': phone, 
                          'name_product': name_product, 'quantity': quantity, 'total': total, 
                          'address': address, 'method_payment': method_payment })

        return redirect('/add_order')
    
    all_order = order.find() 
    return render_template('add_order.html', order=all_order)

@app.post("/<id>/deleteOrder/")
def delete_order(id):
    user.delete_one({"_id": ObjectId(id)})
    return redirect('/add_order')