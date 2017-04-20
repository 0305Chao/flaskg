# coding=utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, \
    BooleanField, SelectField, TextField
from wtforms.validators import Required, Length, Email, Regexp


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
    about_me = TextField('About Me')
    submit = SubmitField()

    def __init__(self, user, *args, **kwds):
        super().__init__(*args, **kwds)
        self.role.choices = [(role.id, role.name) \
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user
