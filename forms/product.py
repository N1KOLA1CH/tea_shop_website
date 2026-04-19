from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ProductForm(FlaskForm):
    title = StringField('Название товара', validators=[DataRequired()])
    description = TextAreaField('Описание')
    price = IntegerField('Цена', validators=[DataRequired()])
    quantity = IntegerField('Количество', validators=[DataRequired(), NumberRange(min=0)])
    submit_publish = SubmitField('Выставить на продажу')
    submit_draft = SubmitField('В черновики')