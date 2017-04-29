# coding=utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, \
    BooleanField, SelectField, TextField, ValidationError
from wtforms.validators import Required, Length, Email, Regexp
from flask_pagedown.fields import PageDownField


class NameForm(FlaskForm):
    name = StringField('你的名字', validators=[Required()])
    submit = SubmitField('Submit')


class EditProfileFrom(FlaskForm):
    name = StringField('Real name', validators=[Required()])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField("About me")
    submit = SubmitField('Submit')


class EditProfileAdminFrom(FlaskForm):
    email = StringField('Email', validators=[Required(),
                                             Length(1, 64), Email()])
    username = StringField('Username', validators=[Required(),
                        Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                            'Username must have only letters, \
                                  numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About Me')
    submit = SubmitField()

    def __init__(self, user, *args, **kwds):
        super().__init__(*args, **kwds)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered!')

    def validate_username(self, field):
        if field.data != self.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already useing')


class PostForm(FlaskForm):
    body = PageDownField('What is your mind?', validators=[Required()])
    submit = SubmitField('Submit')
