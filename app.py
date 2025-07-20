from flask import *
from flask import Flask, render_template
from flask import request, redirect, url_for
from flask import flash
from flask_login import LoginManager
from flask_login import UserMixin, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy # type: ignore
from models import User  

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'Chave1234'

db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro')
def register():
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            flash('Login com sucesso', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')