# coding=utf-8
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from ..models import User
from .forms import LoginForm, RegisterForm, ChangePasswordForm, \
            ChangeEmailForm, PasswordResetRequestForm, PasswordResetForm
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
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirem Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('新的邮件已经发送')
    return redirect(url_for('main.index'))

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('密码已经更改')
            return redirect(url_for('main.index'))
        else:
            flash('密码无效')
    return render_template('auth/change_password.html', form=form)

@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_confirmation_token()
            send_email(user.email, '重置密码', 'auth/email/reset_password',
                        user=user, token=token,
                        next = request.args.get('next'))
        flash('重置密码的邮件已经发送到你的邮箱')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            return redirect(url_for('main.index'))
        print(form.password.data)
        if user.reset_password(token, form.password.data):
            flash('密码重置成功')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_confirmation_token(new_email)
            send_email(new_email, '确认邮箱地址', 'auth/email/change_email',
                        user=current_user, token=token)
            flash('请查看你的邮件， 并尽快确认！')
            return redirect(url_for('main.index'))
        else:
            flash('密码错误')
    return render_template('auth/change_email.html', form=form)

@auth.route('/change-email/<token>', methods=['GET', "POST"])
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('你的邮箱已经更改啦')
    else:
        flash('请求无效')
