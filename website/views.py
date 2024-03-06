from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import Product
from . import db, ALLOWED_EXTENSIONS, UPLOAD_FOLDER
import json
import os

##############
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file(request):
        # check if the post request has the file part
        if 'prod-pic' not in request.files:
            print(request.form.get('prod-pic'))
            flash('No file part')
            return False, ''
        file = request.files['prod-pic']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return False, ''
        if not allowed_file(file.filename):
            flash('Filename not allowed')
            return False, ''
        else:
            filename = secure_filename(file.filename)
            saved_at = os.path.join(UPLOAD_FOLDER, filename)
            file.save(os.path.join("website",saved_at))
            return True, saved_at
#############


views = Blueprint('views', __name__)


@views.route('/admin', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        description = request.form.get('prod-description')#Gets the product from the HTML
        name = request.form.get('prod-name')#Gets the product from the HTML
        price = request.form.get('prod-price')#Gets the product from the HTML
        pic_is_uploaded, uploaded_where = upload_file(request=request)

        n = Product.query.filter_by(name=name).first()
        if n:
            flash('Product already exists!', category='error')
        elif len(description) < 1:
            flash('Description is too short!', category='error')
        elif len(name) < 1:
            flash('Name is too short!', category='error')
        elif int(price) < 1:
            flash('Price must be positive!', category='error')
        elif not pic_is_uploaded:
            flash(f'Problem uploading file {uploaded_where}!', category='error')
        else:
            new_product = Product(name=name,
                                  description=description,
                                  price=price,
                                  pic_uri=uploaded_where,
                                  user_id=current_user.id)  #providing the schema for the product
            db.session.add(new_product) #adding the product to the database
            db.session.commit()
            flash('Product added!', category='success')

    return render_template("home.html", user=current_user)

@views.route('/checkout')
def checkout(user, address, total):
    render_template("checkout.html", user=current_user, address=address, total=total)



@views.route('/shop', methods=['GET', 'POST'])
def shop():
    products = Product.query.all()
    if request.method == 'POST':
        print('POSiiiiT')
        total = 0
        for p in products:
            print("----")
            print(p.name)
            quantity = request.form.get(str(p.id)+'-quantity')
            quantity = 0 if not quantity else quantity
            print(quantity)
            price = p.price
            print(p.price)
            print("----")
            total += int(price)*int(quantity)
            address = request.form.get('address')
            customer_name = request.form.get('customerName')
        return render_template("checkout.html", user=current_user, address=address, total=total)

    return render_template("shop.html", user=current_user, products=products)


@views.route('/delete-product', methods=['POST'])
@login_required
def delete_product():
    rd = json.loads(request.data) # this function expects a JSON from the INDEX.js file
    pId = rd['productId']
    product = Product.query.get(pId)
    if product:
        if product.user_id == current_user.id:
            db.session.delete(product)
            db.session.commit()

    return jsonify({})

@views.route('/', methods=['GET', 'POST'])
def landing():
    return redirect(url_for('views.shop'))
