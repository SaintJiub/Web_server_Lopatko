import sqlite3


class DB:
    def __init__(self):
        conn = sqlite3.connect('news.db', check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


class UserModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash) 
                          VALUES (?,?)''', (user_name, password_hash))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = "+str(user_id))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def exists(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?", (user_name, password_hash))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False, None)


class NewsModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS news 
                                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                   title VARCHAR(100),
                                   content VARCHAR(1000),
                                   user_id INTEGER
                                   )''')
        cursor.close()
        self.connection.commit()

    def insert(self, title, content, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO news 
                            (title, content, user_id) 
                            VALUES (?,?,?)''', (title, content, str(user_id)))
        cursor.close()
        self.connection.commit()

    def get(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM news WHERE id = "  + str(news_id))
        row = cursor.fetchone()
        return row

    def get_all(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT * FROM news WHERE user_id = " + (str(user_id)) + " ORDER BY id DESC")
        else:
            cursor.execute("SELECT * FROM news")
        rows = cursor.fetchall()
        return rows

    def delete(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM news WHERE id = ''' + str(news_id))
        cursor.close()
        self.connection.commit()



class TicketModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS tickets 
                                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                   racename VARCHAR(100),
                                   content VARCHAR(100),
                                   value INTEGER
                                   )''')
        cursor.close()
        self.connection.commit()

    def insert(self, title, content, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO tickets
                            (racename, content, value) 
                            VALUES (?,?,?)''', (title, content, str(user_id)))
        cursor.close()
        self.connection.commit()

    def get(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM tickets WHERE id =" + str(news_id))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM tickets")
        rows = cursor.fetchall()
        return rows

    def delete(self, ticker_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM tickets WHERE id = ''' + str(ticker_id))
        cursor.close()
        self.connection.commit()

    def buy(self, ticker_id):
        data = self.get(ticker_id)
        cursor = self.connection.cursor()
        cursor.execute('''UPDATE tickets set value='''+str(data[3]-1)+''' WHERE id = ''' + str(ticker_id))
        cursor.close()
        self.connection.commit()
        return data[3]-1


db = DB()
user_model = UserModel(db.get_connection())
news_model = NewsModel(db.get_connection())
tickets_model = TicketModel(db.get_connection())
user_model.init_table()
tickets_model.init_table()

from flask import Flask, redirect, render_template, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_test = PasswordField('Повторите пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    back = SubmitField('Назад')
    reg = SubmitField('Зарегистрироваться')


class AddNewsForm(FlaskForm):
    title = StringField('Заголовок новости', validators=[DataRequired()])
    content = TextAreaField('Текст новости', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class AddTicketForm(FlaskForm):
    title = StringField('Рейс', validators=[DataRequired()])
    content = TextAreaField('Текст', validators=[DataRequired()])
    value = StringField('Количество мест', validators=[DataRequired()])
    submit = SubmitField('Добавить')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
user_id = None
user_status = False


# http://127.0.0.1:8080/login
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    global user_id, user_status
    form = LoginForm()
    user_status, user_id = user_model.exists(form.username.data, form.password.data)

    if form.validate_on_submit() and user_status:
        id, name, password = user_model.get(user_id)
        if name == 'lopatko' and id ==1:
            session['user_admin']= True
        else:

            session['user_admin']= False
        return redirect('/index')
    return render_template('login.html', title='Авторизация', form=form)


# http://127.0.0.1:8080/register
@app.route('/register', methods=['GET', 'POST'])
def register():
    global user_id, user_status
    form = RegForm()
    if form.back.data:
        return redirect('/login')
    elif form.reg.data:
        if form.validate_on_submit():
            user_model.insert(form.username.data, form.password.data)
            return redirect('/login')
    return render_template('register.html', title='Авторизация', form=form)


@app.route('/index')
@app.route('/news')
def news():
    if user_status:
        print(session)
        tickets = tickets_model.get_all()
        return render_template('news.html', tickets=tickets)
    else:
        return redirect('/login')


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if not user_status:
        return redirect('/login')
    form = AddNewsForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        news_model.insert(title, content, user_id)
        return redirect("/index")
    return render_template('add_news.html', title='Добавление новости', form=form, username=user_id)


@app.route('/delete_news/<int:news_id>', methods=['GET'])
def delete_news(news_id):
    if not user_status:
        return redirect('/login')
    news_model.delete(news_id)
    return redirect("/index")


@app.route('/add_ticket', methods=['GET', 'POST'])
def add_ticket():
    if not user_status:
        return redirect('/login')
    form = AddTicketForm()
    if form.validate_on_submit():
        racename = form.title.data
        value = form.value.data
        content = form.content.data
        tickets_model.insert(racename, content, value)
        return redirect("/index")
    return render_template('add_ticket.html', title='Добавление билета', form=form, username=user_id)


@app.route('/delete_ticket/<int:ticket_id>', methods=['GET'])
def delete_ticket(ticket_id):
    if not user_status:
        return redirect('/login')
    tickets_model.delete(ticket_id)
    return redirect("/index")


@app.route('/buy_ticket/<int:ticket_id>', methods=['GET'])
def buy_ticket(ticket_id):
    if not user_status:
        return redirect('/login')
    if  tickets_model.buy(ticket_id) <=0:
        tickets_model.delete(ticket_id)
    return redirect("/index")


if __name__ == '__main__':
    app.run(port=8081, host='127.0.0.1', debug=True)
