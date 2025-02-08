from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
# Импорт необходимых модулей из Flask:
# - Flask: основной класс для создания веб-приложения.
# - render_template: функция для рендеринга HTML-шаблонов.
# - request: объект, который содержит данные HTTP-запроса.
# - redirect: функция для перенаправления пользователя на другую страницу.
# - url_for: функция для генерации URL-адресов на основе имени функции-обработчика.

from flask_sqlalchemy import SQLAlchemy
# Импорт SQLAlchemy для работы с базой данных через ORM (Object-Relational Mapping).

app = Flask(__name__)
# Создание экземпляра Flask-приложения. __name__ передается для определения корневого пути приложения.

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://vlados:123@localhost/voting_app'
# Настройка URI для подключения к базе данных PostgreSQL. 
# Формат строки подключения: postgresql://username:password@localhost/dbname

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Отключение отслеживания изменений в SQLAlchemy, чтобы избежать лишних накладных расходов.

app.config['SECRET_KEY'] = 'ваш_секретный_ключ'  # Добавляем секретный ключ

db = SQLAlchemy(app)
# Создание экземпляра SQLAlchemy, который будет использоваться для взаимодействия с базой данных.


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  # Увеличиваем длину поля до 256исмволов в поле password

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    options = db.relationship('Option', backref='poll', lazy=True)

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), nullable=False)
    votes = db.Column(db.Integer, default=0)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)

with app.app_context():
    db.create_all()
# Создание всех таблиц в базе данных, определенных в моделях. 
# app.app_context() обеспечивает контекст приложения, необходимый для работы с базой данных.

@app.route('/')
def home():
    polls = Poll.query.all()
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return render_template('home.html', polls=polls, user=user)

@app.route('/create', methods=['GET', 'POST'])
def create_poll():
    if request.method == 'POST':
        # Получаем данные из формы
        question = request.form['question']
        options = request.form['options'].split(',')  # Разделяем варианты ответа
        # Создаем новый опрос
        new_poll = Poll(question=question)
        db.session.add(new_poll)
        db.session.commit()
        # Создаем варианты ответа
        for option_text in options:
            option = Option(text=option_text.strip(), poll_id=new_poll.id)
            db.session.add(option)
        db.session.commit()
        # Перенаправляем на главную страницу
        return redirect(url_for('home'))
    # Если метод GET, отображаем форму
    return render_template('create_poll.html')

@app.route('/vote/<int:poll_id>', methods=['GET', 'POST'])
def vote(poll_id):
    poll = Poll.query.get_or_404(poll_id)  # Получаем опрос по ID
    if request.method == 'POST':
        # Получаем выбранный вариант ответа
        option_id = request.form['option']
        option = Option.query.get(option_id)
        # Увеличиваем количество голосов
        option.votes += 1
        db.session.commit()
        # Перенаправляем на страницу с результатами
        return redirect(url_for('results', poll_id=poll.id))
    # Если метод GET, отображаем форму для голосования
    return render_template('vote.html', poll=poll)

@app.route('/results/<int:poll_id>')
def results(poll_id):
    poll = Poll.query.get_or_404(poll_id)  # Получаем опрос по ID
    return render_template('results.html', poll=poll)

    # Маршрут для регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Проверяем, существует ли пользователь с таким именем
        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует')
            return redirect(url_for('register'))
        # Создаем нового пользователя
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация прошла успешно. Теперь вы можете войти.')
        return redirect(url_for('login'))
    return render_template('register.html')

# Маршрут для входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        # Проверяем, существует ли пользователь и правильный ли пароль
        if user and user.check_password(password):
            session['user_id'] = user.id  # Сохраняем ID пользователя в сессии
            flash('Вход выполнен успешно')
            return redirect(url_for('home'))
        flash('Неверное имя пользователя или пароль')
        return redirect(url_for('login'))
    return render_template('login.html')

# Маршрут для выхода
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Удаляем ID пользователя из сессии
    flash('Вы вышли из системы')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
# Запуск Flask-приложения, если скрипт выполняется напрямую (а не импортируется как модуль).
# - host='0.0.0.0': приложение будет доступно на всех IP-адресах.
# - debug=True: включение режима отладки, который позволяет видеть ошибки в браузере и автоматически перезагружает сервер при изменении кода.