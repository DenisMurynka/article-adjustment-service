from flask import Flask,render_template,url_for,request,redirect,flash,jsonify,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import  and_
import json
import  sqlalchemy
import sqlite3
import flask_login
from flask_login import UserMixin,LoginManager,login_user,logout_user,login_required
from werkzeug.security import check_password_hash,generate_password_hash
from datetime import datetime as dt,timedelta
import jwt  #specified version== 1.7.1
from functools import wraps
import sys   #cant use COKIES for handling token  ,because of cant import flask_extended ...

app = Flask(__name__)
app.secret_key='some secret salt'
#app.config['SECRET_KEY'] = 'some secret salt'
login_manager = LoginManager()
login_manager.init_app(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///articles_adjustment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  #if you see notice 'SQLALCHEMY_TRACK_MODIFICATIONS'--> add this config,it is not important thought
db = SQLAlchemy(app)
#manager = LoginManager(app)


class Articles(db.Model):
        id = db.Column(db.Integer,primary_key = True)
        title = db.Column(db.String(100),nullable = False)
        intro = db.Column(db.String(300),nullable = False)
        likes = db.Column(db.Integer)
        dislikes = db.Column(db.Integer)
        text = db.Column(db.Text,nullable=False)
        date = db.Column(db.DateTime, default=dt.utcnow)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)

        def __repr__(self):
            return '<Articles %r>' % self.id

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    login = db.Column(db.String(32),nullable=False,unique=False)
    password = db.Column(db.String(255),nullable=False)
    lastSeen = db.Column(db.DateTime)
    lastVisit = db.Column(db.DateTime) #try to migrate to ActionEvent


class ActionEvent(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    action = db.Column(db.String(32), nullable=False)
    date = db.Column(db.DateTime, default=dt.utcnow)


def visits():

    data = jwt.decode((sys.argv[1])['token'], app.config['SECRET_KEY'])
    user = User.query.filter_by(id=data['public_id']).first()
    user.lastVisit = dt.now()
    db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id) #get_or_404?

def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
       # tmp=(sys.argv[0])
       # print(tmp['token'].decode("utf-8") )
        print(sys.argv)
       # token=tmp['token'].decode("utf-8")

        token=((sys.argv[1])['token']).decode("utf-8")
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            jwt.decode(token,app.config['SECRET_KEY'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args,**kwargs)
    return decorated



@app.route('/analitics')# http://127.0.0.1:5000/analitics?dateFrom=2019-10-01&dateTo=2022-01-01
def analytics_statist():
    visits()

    dateFrom = request.args.get('dateFrom')
    dateTo = request.args.get('dateTo')
    result = db.session.execute("SELECT * from articles as A WHERE A.date >= :val and A.date <= :val2", {'val': dateFrom, 'val2': dateTo})


    return jsonify({'result': [dict(row) for row in result]})


@app.route('/like/<int:postId>')
def like(postId):
   visits()

   article = Articles.query.filter_by(id=postId).first()
   data = jwt.decode((sys.argv[1])['token'],app.config['SECRET_KEY'])

   actionEvent_like = ActionEvent(user_id=data['public_id'],
                             article_id=article.id,
                             action='like')

   article.likes += 1
   db.session.commit()
   db.session.add(actionEvent_like)
   db.session.commit()
   return redirect("/posts")

@app.route('/dislike/<int:postId>')
def dislike(postId):
   visits()
   article = Articles.query.filter_by(id=postId).first()
   data = jwt.decode((sys.argv[1])['token'], app.config['SECRET_KEY'])

   actionEvent = ActionEvent(user_id=data['public_id'],
                             article_id=article.id,
                             action='dislike')

   article.likes -= 1
   article.dislikes += 1
   db.session.add(actionEvent)
   db.session.commit()
   return redirect("/posts")


@app.route('/')
@app.route('/home')
def index():
    visits()
    return render_template('index.html')


@app.route('/about')
@login_required
def about():
    visits()
    return render_template('about.html')


@app.route('/posts')
@flask_login.login_required
def posts():
    visits()
    articles = Articles.query.order_by(Articles.date.desc()).all()
    return render_template("posts.html", articles=articles)

@app.route('/posts/<int:id>')
def posts_text(id):
    visits()

    article = Articles.query.get(id)
    return render_template("post_text.html", article=article)


@app.route('/posts/<int:id>/del')
def posts_delete(id):
    visits()

    article = Articles.query.get_or_404(id)
    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/posts')
    except:
        return 'Cant delete or 404'


@app.route('/create-article', methods=['POST','GET'])
@token_required
def create_article():
    visits()

    if request.method == "POST" and user:
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']
        data = jwt.decode((sys.argv[1])['token'], app.config['SECRET_KEY'])

        article = Articles(title=title,
                           intro=intro,
                           text=text,
                           user_id=data['public_id'])
        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/posts')
        except:
            return "Cant add your article"
    else:
        return render_template("create-article.html")

@app.route('/posts/<int:id>/update', methods=['POST','GET'])
def post_update(id):
    visits()

    article = Articles.query.get(id)
    if request.method == "POST":
        article.title = request.form['title']
        article.intro = request.form['intro']
        article.text = request.form['text']

        try:
            db.session.commit()
            return redirect('/posts')
        except:
            return "Cant update"
    else:

        return render_template("post_update.html",article=article)

@app.route('/user/<string:name>/<int:id>')
def user(name, id):
    visits()
    return "User  "+name+'--'+str(id)

@app.route('/login', methods=['GET', 'POST'])
def login_page():

    login = request.form.get('login')
    password = request.form.get('password')

    if login and password:
        user = User.query.filter_by(login=login).first()
        if  user and check_password_hash(user.password, password):
            token = jwt.encode({'public_id': user.id, 'exp': dt.utcnow() + timedelta(minutes=10)}, app.config['SECRET_KEY'])
            sys.argv.append({'token': token})

            login_user(user)
            visits()
            #next_page = request.args.get('next')
            user.lastSeen = dt.now()

            db.session.commit()
            return redirect(url_for('posts'))

        else:
            flash('Login or password is not correct')
    else:
        flash('Please fill login and password fields')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():

    visits()

    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if request.method == 'POST':
        if not (login or password or password2):
            flash('Please, fill all fields!')
        elif password != password2:
            flash('Passwords are not equal!')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login_page'))

    return render_template('register.html')

@app.route('/logout', methods=['GET', 'POST'])
#@login_required
def logout():
    visits()
    logout_user()
    return redirect(url_for('index'))


@app.route('/None')
#@login_required
def none():
    return render_template('index.html')

@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)

    return response


if __name__ == "__main__":
    #db.create_all()
    app.run(debug=True) #dev errors expected with debug mode
