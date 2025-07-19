from flask import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro')
def register():
    return render_template('cadastro.html')

@app.route('/login')
def login():
    return render_template('login.html')
