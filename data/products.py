import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm

class Product(SqlAlchemyBase):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    quantity = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    is_deleted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    image_data = sqlalchemy.Column(sqlalchemy.BLOB)
    is_published = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    tea_type = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    ratings = orm.relationship("Rating", backref="product")

    @property
    def average_rating(self):
        if not self.ratings:
            return 0

        user_ratings = {}
        for r in self.ratings:
            if r.user_id not in user_ratings:
                user_ratings[r.user_id] = []
            user_ratings[r.user_id].append(r.value)

        user_averages = []
        for ratings_list in user_ratings.values():

            avg_for_user = sum(ratings_list) / len(ratings_list)
            user_averages.append(avg_for_user)


        return round(sum(user_averages) / len(user_averages), 1)

    @property
    def ratings_count(self):
        if not self.ratings:
            return 0

        unique_users = set(r.user_id for r in self.ratings)
        return len(unique_users)