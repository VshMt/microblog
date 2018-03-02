from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from wtforms import TextAreaField
from wtforms.validators import Length
from app.models import User
from flask_babel import lazy_gettext as _l
from flask_login import LoginManager
import logging

class LoginForm(FlaskForm):
    username = StringField(_l('Имя пользователя'), validators=[DataRequired()])
    password = PasswordField(_l('Пароль'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Запомнить меня'))
    submit = SubmitField(_l('Войти'))

class RegistrationForm(FlaskForm):
    username = StringField(_l('Имя пользователя'), validators=[DataRequired()])
    email = StringField(_l('Эл.почта'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Пароль'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Повтор пароля'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Зарегистрировать'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l('Пожалуйста введите другое имя пользователя.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_l('Пожалуйста введите другой адрес.'))

class EditProfileForm(FlaskForm):
    username = StringField(_l('Имя пользователя'), validators=[DataRequired()])
    about_me = TextAreaField(_l('О себе'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Сохранить изменения'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_l('Пожалуйста измените имя пользователя.'))

class PostForm(FlaskForm):
    post = TextAreaField(_l('Напишите что-нибудь'), validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Отправить'))

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Запрос Сброса Пароля'))

class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Пароль'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Повторите Пароль'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Запрос Сброса Пароля'))