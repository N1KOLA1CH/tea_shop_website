from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange

class RegisterForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired(), Email(message='Неверный формат почты')])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password', message='Пароли не совпадают')])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

class DepositForm(FlaskForm):
    amount = IntegerField('Сумма пополнения (₽)', validators=[
        DataRequired(message="Введите сумму"),
        NumberRange(min=10, message="Минимальная сумма — 10 ₽", max=1000000)
    ])
    submit = SubmitField('Пополнить баланс')