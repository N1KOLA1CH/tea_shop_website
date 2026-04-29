from flask import Flask, render_template, redirect, abort, request, flash
from data import db_session
from data.ratings import Rating
from data.users import User
from data.basket import Basket
from forms.user import RegisterForm, DepositForm
from flask_login import LoginManager
from forms.login import LoginForm
from flask_login import login_user, logout_user, login_required, current_user
from data.products import Product
from data.orders import Order
from forms.product import ProductForm
import base64
from flask_restful import Api
from api import products_resource

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

api = Api(app)

api.add_resource(products_resource.ProductsListResource, '/api/products')
api.add_resource(products_resource.ProductsResource, '/api/products/<int:product_id>')

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.get(User, user_id)
    db_sess.close()
    return user


@app.route('/')
def index():
    db_sess = db_session.create_session()


    selected_type = request.args.get('tea_type')


    query = db_sess.query(Product).filter(
        Product.is_published == True,
        Product.is_deleted == False
    )


    if selected_type and selected_type != "Все":
        query = query.filter(Product.tea_type == selected_type)

    products = query.all()


    for item in products:
        if item.image_data:
            item.img_str = base64.b64encode(item.image_data).decode('utf-8')
        else:
            item.img_str = None

    basket_data = {}
    if current_user.is_authenticated:
        items = db_sess.query(Basket).filter(Basket.user_id == current_user.id).all()
        basket_data = {item.product_id: item.quantity for item in items}


    return render_template('index.html',
                           products=products,
                           basket_data=basket_data,
                           selected_type=selected_type)


@app.route('/remove_one/<int:product_id>')
@login_required
def remove_one(product_id):
    db_sess = db_session.create_session()
    item = db_sess.query(Basket).filter(Basket.product_id == product_id,
                                        Basket.user_id == current_user.id).first()
    if item:
        item.product.quantity += 1
        if item.quantity > 1:
            item.quantity -= 1
        else:
            db_sess.delete(item)

        db_sess.commit()

    return redirect(request.referrer or '/')


@app.context_processor
def inject_cart_count():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        try:
            count = db_sess.query(Basket).filter(Basket.user_id == current_user.id).count()
            return dict(cart_items_count=count)
        finally:
            db_sess.close()
    return dict(cart_items_count=0)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@gmail.com':
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
        if not user:
            return render_template('login.html',
                                   message='Такого пользователя не существует',
                                   form=form)
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)

            return redirect("/")

        return render_template('login.html',
                               message='Неправильный логин или пароль',
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
        is_published = form.submit_publish.data and form.quantity.data > 0

        product = Product(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            tea_type=form.tea_type.data,
            quantity=form.quantity.data,
            is_published=is_published
        )

        if form.image.data:
            product.image_data = form.image.data.read()

        db_sess.add(product)
        db_sess.commit()
        return redirect('/') if is_published else redirect('/drafts')

    return render_template('add_product.html', title='Добавление товара', form=form)


@app.route('/drafts')
@login_required
def drafts():
    if not current_user.is_admin:
        abort(403)
    db_sess = db_session.create_session()
    products = db_sess.query(Product).filter(Product.is_published == False).all()

    for item in products:
        item.img_str = base64.b64encode(item.image_data).decode('utf-8') if item.image_data else None

    return render_template('index.html', title='Черновики', products=products)


@app.route('/delete_product/<int:id>')
@login_required
def delete_product(id):
    if not current_user.is_admin:
        abort(403)

    db_sess = db_session.create_session()
    product = db_sess.query(Product).get(id)
    if product:
        product.is_deleted = True
        db_sess.commit()

    return redirect('/')


@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    if not current_user.is_admin:
        abort(403)

    form = ProductForm()
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == id).first()

    if not product:
        abort(404)

    if request.method == "GET":
        form.title.data = product.title
        form.description.data = product.description
        form.tea_type.data = product.tea_type
        form.price.data = product.price
        form.quantity.data = product.quantity

    if form.validate_on_submit():
        product.title = form.title.data
        product.tea_type = form.tea_type.data
        product.description = form.description.data
        product.price = form.price.data
        product.quantity = form.quantity.data

        if form.image.data:
            product.image_data = form.image.data.read()

        product.is_published = True if form.submit_publish.data else False

        db_sess.commit()
        return redirect('/')

    return render_template('add_product.html', title='Редактирование товара', form=form)

    return render_template('add_product.html', title='Редактирование товара', form=form)


@app.route('/cart')
@login_required
def cart():
    db_sess = db_session.create_session()

    basket_items = db_sess.query(Basket).filter(Basket.user_id == current_user.id).all()

    total_price = sum(item.product.price * item.quantity for item in basket_items)

    return render_template('cart.html', title='Корзина',
                           basket=basket_items, total_price=total_price)


@app.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == product_id).first()

    if product and product.quantity > 0:
        product.quantity -= 1

        item = db_sess.query(Basket).filter(Basket.product_id == product_id,
                                            Basket.user_id == current_user.id).first()
        if item:
            item.quantity += 1
        else:
            new_item = Basket(product_id=product_id, user_id=current_user.id)
            db_sess.add(new_item)
        db_sess.commit()

    return redirect(request.referrer or '/')


@app.route('/delete_from_cart/<int:basket_id>')
@login_required
def delete_from_cart(basket_id):
    db_sess = db_session.create_session()

    item = db_sess.query(Basket).filter(Basket.id == basket_id,
                                        Basket.user_id == current_user.id).first()

    if item:
        item.product.quantity += item.quantity

        db_sess.delete(item)
        db_sess.commit()

    return redirect('/cart')


@app.route('/confirm_order')
@login_required
def confirm_order():
    db_sess = db_session.create_session()
    basket_items = db_sess.query(Basket).filter(Basket.user_id == current_user.id).all()

    if not basket_items:
        return redirect('/cart')

    total_price = sum(item.product.price * item.quantity for item in basket_items)

    return render_template('confirm_order.html',
                           title='Подтверждение заказа',
                           basket=basket_items,
                           total=total_price)


@app.route('/pay_order', methods=['POST'])
@login_required
def pay_order():
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    basket_items = db_sess.query(Basket).filter(Basket.user_id == current_user.id).all()

    if not basket_items:
        return redirect('/cart')

    total_price = sum(item.product.price * item.quantity for item in basket_items)

    if user.balance >= total_price:
        user.balance -= total_price
        for item in basket_items:
            order = Order(
                user_id=user.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=item.product.price
            )
            db_sess.add(order)
            db_sess.delete(item)
        db_sess.commit()

        flash("Покупка успешно совершена!", "success")
        return redirect('/profile')
    else:

        flash(f"Недостаточно средств! Нужно {total_price} ₽, а у вас {user.balance} ₽", "danger")
        return redirect('/cart')


@app.route('/profile')
@login_required
def profile():
    db_sess = db_session.create_session()
    orders = db_sess.query(Order).filter(Order.user_id == current_user.id).order_by(Order.purchase_date.desc()).all()
    rated_order_ids = [r.order_id for r in db_sess.query(Rating).filter(Rating.user_id == current_user.id).all()]
    for order in orders:
        if order.product.image_data:
            order.product.img_str = base64.b64encode(order.product.image_data).decode('utf-8')
        else:
            order.product.img_str = None

    return render_template('profile.html', title='Личный кабинет',
                           orders=orders, rated_orders=rated_order_ids)


@app.route('/admin/history')
@login_required
def admin_history():
    if not current_user.is_admin:
        return redirect('/')
    db_sess = db_session.create_session()
    orders = db_sess.query(Order).order_by(Order.purchase_date.desc()).all()
    for order in orders:
        if order.product.image_data:
            order.product.img_str = base64.b64encode(order.product.image_data).decode('utf-8')
        else:
            order.product.img_str = None

    return render_template('admin_history.html', title='Логи покупок', orders=orders)


@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    form = DepositForm()
    db_sess = db_session.create_session()

    if form.validate_on_submit():
        user = db_sess.query(User).get(current_user.id)
        user.balance += form.amount.data
        db_sess.commit()

        flash(f"Баланс успешно пополнен на {form.amount.data} ₽!", "success")
        return redirect('/profile')

    return render_template('deposit.html', title='Пополнение баланса', form=form)


@app.route('/rate_product/<int:order_id>/<int:value>')
@login_required
def rate_product(order_id, value):
    if value < 1 or value > 5:
        abort(400)
    db_sess = db_session.create_session()

    order = db_sess.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        flash("Заказ не найден!", "danger")
        return redirect('/profile')

    existing = db_sess.query(Rating).filter(Rating.order_id == order_id).first()
    if existing:
        flash("Этот заказ уже оценен!", "warning")
    else:

        new_rating = Rating(product_id=order.product_id,
                            user_id=current_user.id,
                            order_id=order_id,
                            value=value)
        db_sess.add(new_rating)
        db_sess.commit()
        flash("Спасибо за оценку!", "success")

    return redirect('/profile')


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.create_session().close()
    
@app.route('/test_ip')
def test_ip():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    return f"Твой текущий IP в сети: {ip}"

if __name__ == '__main__':
    db_session.global_init('db/shop.db')
    db_sess = db_session.create_session()
    admin = db_sess.query(User).filter(User.email == 'admin@gmail.com').first()
    if not admin:
        admin = User(name="Администратор",
                     email='admin@gmail.com',
                     balance=9999999,
                     is_admin=True)
        admin.set_password('admin')
        db_sess.add(admin)
        db_sess.commit()
    db_sess.close()
    app.run(port=5000, host='0.0.0.0')
