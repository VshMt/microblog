# -*- coding: utf-8 -*- 
from flask import render_template, flash, redirect, url_for
from flask import request
from flask import g
from flask_login import current_user, login_user
from flask_login import logout_user, login_required
from app import app
from app import db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from app.forms import ResetPasswordRequestForm
from app.forms import ResetPasswordForm
from app.email import send_password_reset_email
from app.models import User, Post
from werkzeug.urls import url_parse
from datetime import datetime
from flask_babel import _
from flask_babel import get_locale
from flask_login import LoginManager
import logging

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Домашняя'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url, edit_profile_flg = False)

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Просмотр'), posts=posts.items, next_url=next_url,
                           prev_url=prev_url, edit_profile_flg = False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Неправильное имя пользователя или пароль'))
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Вход', form=form, edit_profile_flg = False)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Подравляем, теперь вы зарегистрированный пользователь!'))
        return redirect(url_for('login'))
    return render_template('register.html', title=_('Регистрация'), form=form, edit_profile_flg = False)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, edit_profile_flg = True)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    app.logger.setLevel(logging.INFO)
    app.logger.info('edit_profile {}\n'.format(current_user.username))
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Ваши изменения сохранены.'))
        return redirect(url_for('edit_profile'))#return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Редактирование Профиля'),
                           form=form, edit_profile_flg = False)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('Пользователь %(username)s не найден.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('ВЫ не можете подписаться на себя!'))
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('Вы подписались на собщения %(username)s.', username=username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('Пользователь %(username)s не найден.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('Вы не можете отписаться от себя!'))
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('Вы больше не подписаны на собщения %(username)s.', username=username))
    return redirect(url_for('user', username=username))

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Проверьте адрес вашей эл.почты для получения инструкций по сбросу пароля'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title=_('Сброс Пароля'), form=form, edit_profile_flg = False)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Ваш пароль будет изменен.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form, edit_profile_flg = False)