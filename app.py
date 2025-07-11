import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
from models import db, Product
from forms import ProductForm
from config import Config
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Admin credentials ---
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "password")

with app.app_context():
    print("Using DB URI:", app.config['SQLALCHEMY_DATABASE_URI'])
    db.create_all()

@app.route('/')
def index():
    query = request.args.get('serial')
    product = None
    if query:
        product = Product.query.filter_by(serial_number=query).first()
    return render_template('index.html', product=product)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    products = Product.query.all()
    return render_template('admin.html', products=products)

@app.route('/add', methods=['GET', 'POST'])
@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def add_or_edit(product_id=None):
    if not session.get('admin'):
        return redirect(url_for('login'))

    product = Product.query.get(product_id) if product_id else None
    form = ProductForm(original_serial_number=product.serial_number if product else None)

    if request.method == 'GET' and product:
        form.serial_number.data = product.serial_number
        form.name.data = product.name
        form.description.data = product.description

    if form.validate_on_submit():
        image_filename = product.image_filename if product else None

        if form.image.data:
            image = form.image.data
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        try:
            if product:
                product.serial_number = form.serial_number.data
                product.name = form.name.data
                product.description = form.description.data
                product.image_filename = image_filename
            else:
                product = Product(
                    serial_number=form.serial_number.data,
                    name=form.name.data,
                    description=form.description.data,
                    image_filename=image_filename
                )
                db.session.add(product)

            db.session.commit()
            return redirect(url_for('admin'))

        except IntegrityError:
            db.session.rollback()
            flash('A product with that serial number already exists. Please use a unique serial number.', 'danger')

    return render_template('form.html', form=form, product=product)

@app.route('/delete/<int:product_id>')
def delete(product_id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.secret_key = app.config['SECRET_KEY']
    app.run(debug=True)
