
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, \
    BooleanField, ValidationError
from wtforms.validators import Required, Email, Length, EqualTo, Regexp
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('Emial', validators=[
                        Required(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegisterForm(FlaskForm):
    email = StringField('Email',
                        validators=[Required(), Length(1, 64), Email()])
    username = StringField('Username',
                           validators=[Required(), Length(1, 64),
                                       Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Username must have only letters, \
                            numbers, dots or underscores')])
    password = PasswordField('Password', validators=[Required(),
                              EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('此邮箱已经注册过了')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('此用户名已经使用')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Old password", validators=[Required()])
    password = PasswordField('New password', validators=[Required(),
                              EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm new password', validators=[Required()])
    submit = SubmitField('更新密码')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[Required(),
                                             Length(1, 64), Email()])
    submit = SubmitField('重置密码')


class PasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[Required(),
                                             Length(1, 64), Email()])
    password = PasswordField('New password', validators=[Required(),
                             EqualTo('password2', message='密码必须一样')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('重置密码')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('哪里来的邮箱')


class ChangeEmailForm(FlaskForm):
    email = StringField('New Email', validators=[Required(),
                        Length(1, 64), Email()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('更换邮箱')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('此邮箱已经注册过啦')
