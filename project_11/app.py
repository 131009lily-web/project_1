import os # <--- ДОБАВИТЬ ЭТУ СТРОКУ
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SECRET_KEY'] = 'a_very_secret_and_hard_to_guess_string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')
db = SQLAlchemy(app)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'



@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':


        print("Форма отправлена (метод POST получен)")
        print(f"ПОЛУЧЕННЫЕ ДАННЫЕ: {request.form}")


        first_name = request.form.get('first')
        last_name = request.form.get('last')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')


        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            return "Пользователь с таким email уже существует!"


        hashed_password = generate_password_hash(password)


        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            password_hash=hashed_password
        )


        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('success', user_id=new_user.id))
        except Exception as e:
            print(f"!!! ОШИБКА ПРИ ЗАПИСИ В БД: {e}")
            return "При регистрации произошла ошибка, смотрите терминал"


    else:
        return render_template('register.html')


@app.route('/success/<int:user_id>')
def success(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('success.html', user=user)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clients')
def clients():
    return render_template('clients.html')

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/landlords')
def landlords():
    return render_template('landlords.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('profile')) # Перенаправляем в профиль
        else:
            flash('Неверный email или пароль', 'danger')
            return redirect(url_for('login')) # Возвращаем на страницу входа

    return render_template('login.html')

@app.route('/masters')
def masters():
    return render_template('masters.html')


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите, чтобы получить доступ к этой странице.', 'warning')
        return redirect(url_for('login'))

    user = User.query.get_or_404(session['user_id'])

    return render_template('profile.html', user=user)


@app.route('/logout')
def logout():
    session.pop('user_id', None)

    flash('Вы успешно вышли из системы.', 'info')

    return redirect(url_for('login'))


if __name__ == '__main__':

    with app.app_context():
        db.create_all()
    app.run(debug=True)