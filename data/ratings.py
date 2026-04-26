import sqlalchemy
from .db_session import SqlAlchemyBase


class Rating(SqlAlchemyBase):
    __tablename__ = 'ratings'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    value = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    order_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("orders.id"))

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    product_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("products.id"))