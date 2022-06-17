from flask import render_template, flash, redirect, url_for
from application.blueprints.forms import LoginForm, RegisterForm
from application.extensions.database import db
from application.models import User



def init_app(app):

    @app.route('/home')
    def home():
        return render_template('home.html')

    @app.route('/', methods=['GET','POST'])
    def signin():
        error=None
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                if user.password == form.password.data:
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