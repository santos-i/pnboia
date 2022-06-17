from flask import render_template, flash, redirect, url_for, session
from application.blueprints.forms import LoginForm, RegisterForm
from application.extensions.database import db
from application.models import User
from application.blueprints.auth import login_required



def init_app(app):

    @app.route('/home')
    @login_required
    def home():
        return redirect(url_for('dash'))

    @app.route('/alcatrazes')
    @login_required
    def dash():
        return 'ok'



    @app.route('/', methods=['GET','POST'])
    def signin():
        error=None
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                if user.password == form.password.data:
                    session['username'] = user.username
                    return redirect(url_for('home'))
                else:

                    error = 'Invalid credentials'
            else:
                error = 'Invalid credentials'    
            
        return render_template('signin.html', form=form, error=error)

    
    @app.route('/signup', methods=['GET','POST'])
    def signup():
        error = None
        form = RegisterForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                error = 'The user already exists'
            else:
                new_user = User(username=form.username.data, password=form.password1.data)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('signin'))
        elif form.password1.data != form.password2.data:
                error = 'Passwords do no match!'

        return render_template('signup.html', form=form, error=error)


    @app.route('/alcatrazes/logout')
    def logout():

        if not session.get('username'):
            return redirect(url_for('signin'))

        session['username'] = False
        session.pop('username',None)
        return redirect(url_for('signin'))
