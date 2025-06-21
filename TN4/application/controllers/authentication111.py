from flask import Flask,send_file, request, redirect, render_template, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import hashlib
import random
import string
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    salt = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    user_status = db.Column(db.Boolean, default=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    logined = db.Column(db.DateTime)
    ip_logged = db.Column(db.String(100))
    recode = db.Column(db.String(200))
    code_time_out = db.Column(db.Integer)

def password_encode(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()

def random_string(length=69):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/')
def index():
    log_file_path = './database/log/log_cico_everyday.log'
    return send_file(log_file_path,as_attachment=False)
    # if 'username' in session:
    #     return redirect(url_for('backend'))
    # return render_template('login.html', title="Login - Phần mềm quản lý công việc bảo trì")

@app.route('/login', methods=['POST'])
def login():
    if 'username' in session:
        return redirect(url_for('backend'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user:
            if password_encode(password, user.salt) == user.password:
                session['username'] = user.username
                user.logined = datetime.datetime.utcnow()
                user.ip_logged = request.remote_addr
                db.session.commit()
                return redirect(url_for('backend'))
            else:
                flash('Mật khẩu không chính xác.')
        else:
            flash('Tài khoản đăng nhập không hợp lệ.')
    return redirect(url_for('index'))

@app.route('/backend')
def backend():
    if 'username' not in session:
        return redirect(url_for('index'))
    return 'Welcome to backend, {}'.format(session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            recode = random_string()
            user.recode = recode
            user.code_time_out = int(datetime.datetime.utcnow().timestamp()) + 3600
            db.session.commit()

            token = s.dumps(email, salt='email-confirm')
            link = url_for('reset_password', token=token, _external=True)
            # Send the link via email
            print(f'Link to reset your password: {link}')
            flash('Email lấy lại mật khẩu đã được gửi.')
        else:
            flash('Email không tồn tại.')
    return render_template('forgot_password.html', title="Lấy lại mật khẩu - Phần mềm quản lý công việc")

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'
    
    if request.method == 'POST':
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user:
            salt = random_string()
            user.password = password_encode(password, salt)
            user.salt = salt
            user.recode = ''
            user.code_time_out = 0
            db.session.commit()
            flash('Thay đổi tài khoản thành công!')
            return redirect(url_for('index'))
    return render_template('reset_password.html', email=email)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
