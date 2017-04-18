# coding=utf-8
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from ..models import User
from .forms import LoginForm, RegisterForm
from . import auth
from ..email import send_email
from .. import db

@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed\
            and request.endpoint[:5] != 'auth.'\
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/login', methods=['GET', "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('错误的密码或用户名')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('退出成功')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username = form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm your acount',
                  'auth/email/confirm', user=user, token=token)
        flash('一封确认邮件发送到了你的邮箱')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('证实邮件成功')
    else:
        flash('确认邮件链接有误或已经过期')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def request_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirem Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('新的邮件已经发送')
    return redirect(url_for('main.index'))
