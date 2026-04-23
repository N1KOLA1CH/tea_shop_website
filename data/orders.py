import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase

class Order(SqlAlchemyBase):
    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    product_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("products.id"))
    quantity = sqlalchemy.Column(sqlalchemy.Integer)
    price_at_purchase = sqlalchemy.Column(sqlalchemy.Integer) # Фиксируем цену на момент покупки
    purchase_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    user = orm.relationship('User')
    product = orm.relationship('Product')