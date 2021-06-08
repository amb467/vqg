from flask import render_template, flash, redirect
from app import app
from app.forms import LoginForm, AnnotationForm

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/index')
    return render_template('login.html', title='Sign In', form=form)
      
@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Amanda'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)
    
@app.route('/annotate', methods=['GET', 'POST'])
def annotate():
    form = AnnotationForm()
    if form.validate_on_submit():
        print("Annotation form submitted!")
    return render_template('annotate.html', form=form)