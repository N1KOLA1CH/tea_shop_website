from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SubmitField, FileField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired, NumberRange

class ProductForm(FlaskForm):
    title = StringField('Название товара', validators=[DataRequired()])
    description = TextAreaField('Описание')
    tea_type = SelectField('Тип чая', choices=[
        ('Белый', 'Белый'),
        ('Зелёный', 'Зелёный'),
        ('Жёлтый', 'Жёлтый'),
        ('Красный', 'Красный'),
        ('Чёрный', 'Чёрный')
    ])
    price = IntegerField('Цена', validators=[DataRequired()])
    quantity = IntegerField('Количество', validators=[DataRequired(), NumberRange(min=0)])
    submit_publish = SubmitField('Выставить на продажу')
    image = FileField('Картинка товара')
    submit_draft = SubmitField('В черновики')