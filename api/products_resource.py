from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.products import Product

class ProductsResource(Resource):
    def get(self, product_id):
        # Получение одного товара по ID
        session = db_session.create_session()
        product = session.query(Product).get(product_id)
        if not product:
            abort(404, message=f"Product {product_id} not found")
        return jsonify({
            'product': {
                'title': product.title,
                'tea_type': product.tea_type,
                'price': product.price,
                'quantity': product.quantity
            }
        })

class ProductsListResource(Resource):
    def get(self):
        # Получение всех товаров
        session = db_session.create_session()
        products = session.query(Product).all()
        return jsonify({
            'products': [
                {
                    'id': item.id,
                    'title': item.title,
                    'tea_type': item.tea_type,
                    'price': item.price
                } for item in products
            ]
        })