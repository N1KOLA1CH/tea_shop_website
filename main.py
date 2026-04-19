from flask import Flask, render_template, redirect, abort
from data import db_session
from data.users import User
from forms.user import RegisterForm
from flask_login import LoginManager
from forms.login import LoginForm
from flask_login import login_user, logout_user, login_required, current_user
from data.products import Product
from forms.product import ProductForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    user =  db_sess.get(User, user_id)
    db_sess.close()
    return user

@app.route('/')
def index():
    db_sess = db_session.create_session()
    products = db_sess.query(Product).filter(Product.is_published == True).all()
    db_sess.close() 
    return render_template('index.html', title='Главная', products=products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.email.data == "admin@gmail.com":
            return render_template('register.html', title='Регистрация', 
                                   form=form, message="Эта почта зарезервирована!")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message='Такой пользователь уже есть')
        
        user = User(name=form.name.data,
                     email=form.email.data,
                      balance=5000,
                      is_admin=False)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not current_user.is_admin:
        abort(403)
    form = ProductForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        is_published = False
        if form.submit_publish.data and form.quantity.data > 0:
            is_published = True
        product = Product(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            quantity=form.quantity.data,
            is_published=is_published
        )
        db_sess.add(product)
        db_sess.commit()
        db_sess.close()
        if is_published:
            return redirect('/')
        else:
            return redirect('/drafts')
    return render_template('add_product.html', title='Добавление товара', form=form)
@app.route('/drafts')
@login_required
def drafts():
    if not current_user.is_admin:
        abort(403)
    db_sess = db_session.create_session()
    # только не опубликованные товары
    products = db_sess.query(Product).filter(Product.is_published == False).all()
    return render_template('index.html', title='Черновики', products=products)

@app.route('/delete_product/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_product(id):
    db_sess = db_session.create_session()

    product = db_sess.query(Product).filter(Product.id == id).first()
    
    if product:
        
        if current_user.is_admin:
            db_sess.delete(product)
            db_sess.commit()
        else:
            abort(403)
    else:
        
        abort(404)
        
    return redirect('/')

if __name__ == '__main__':
    db_session.global_init("db/shop.db")
    db_sess = db_session.create_session()
    admin = db_sess.query(User).filter(User.email == "admin@gmail.com").first()
    if not admin:
        admin = User(name="Администратор",
        email="admin@gmail.com",
        balance=9999999,
        is_admin=True)
        admin.set_password("admin")
        db_sess.add(admin)
        db_sess.commit()
    db_sess.close()
    app.run(port=8080, host='127.0.0.1') 