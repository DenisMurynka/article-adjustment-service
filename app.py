from flask import Flask,render_template,url_for,request,redirect,flash,jsonify
from flask_sqlalchemy import SQLAlchemy

from flask_login import UserMixin,LoginManager,login_user,logout_user,login_required
from werkzeug.security import check_password_hash,generate_password_hash
from datetime import datetime as dt,timedelta
import jwt  #specified version== 1.7.1
from functools import wraps
import sys
app = Flask(__name__)
#app.secret_key='some secret salt'
app.config['SECRET_KEY'] = 'some secret salt'
app.config['JWT_LOCATION'] = ['COOKIES']
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
app.config['JWT_COOKIE_CSRF_PROTECT'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///articles_adjustment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  #if you see notice 'SQLALCHEMY_TRACK_MODIFICATIONS'--> add this config,it is not important thought
db = SQLAlchemy(app)
manager = LoginManager(app)



class Articles(db.Model):
        id = db.Column(db.Integer,primary_key = True)
        title = db.Column(db.String(100),nullable = False)
        intro = db.Column(db.String(300),nullable = False)
        likes = db.Column(db.Integer)
        dislikes = db.Column(db.Integer)
        text = db.Column(db.Text,nullable = False)
        date = db.Column(db.DateTime, default = dt.utcnow)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)



        def __repr__(self):
            return '<Articles %r>' % self.id

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    login = db.Column(db.String(32),nullable=False,unique=False)
    password = db.Column(db.String(255),nullable=False)



def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        #tmp=(sys.argv[1])
        #print(tmp['token'].decode("utf-8") )
        #token=tmp['token'].decode("utf-8")
        token=((sys.argv[1])['token']).decode("utf-8")
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            data=jwt.decode(token,app.config['SECRET_KEY'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args,**kwargs)
    return decorated

@app.route('/like/<int:postId>')
def like(postId):

   article = Articles.query.filter_by(id=postId).first()
   article.likes += 1
   db.session.commit()
   return redirect("/posts")

@app.route('/dislike/<int:postId>')
def dislike(postId):

   article = Articles.query.filter_by(id=postId).first()
   article.likes -= 1
   article.dislikes += 1
   db.session.commit()
   return redirect("/posts")



@manager.user_loader
def load_user(user_id):#id?
    return User.query.get(user_id) #get_or_404?

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/about')
#@login_required
def about():
    return render_template('about.html')


@app.route('/posts')
@token_required
def posts():
    #print('lolllll')
    articles = Articles.query.order_by(Articles.date.desc()).all()
    return render_template("posts.html", articles=articles)

@app.route('/posts/<int:id>')
def posts_text(id):

    article = Articles.query.get(id)
    return render_template("post_text.html", article=article)


@app.route('/posts/<int:id>/del')
def posts_delete(id):

    article = Articles.query.get_or_404(id)
    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/posts')
    except:
        return 'Cant delete or 404'


@app.route('/create-article', methods=['POST','GET'])
@login_required
def create_article():
    if request.method == "POST" and user:
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        article = Articles(title = title,
                           intro = intro,
                           text  = text)
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
    article = Articles.query.get(id)
    if request.method == "POST":
        article.title = request.form['title']
        article.intro = request.form['intro']
        article.text = request.form['text']

        # article = Articles(title = title,
        #                    intro = intro,
        #                    text  = text)
        try:
            #db.session.add(article)
            db.session.commit()
            return redirect('/posts')
        except:
            return "Cant update"
    else:

        return render_template("post_update.html",article=article)

@app.route('/user/<string:name>/<int:id>')
def user(name, id):
    return "User  "+name+'--'+str(id)



@app.route('/login', methods=['GET', 'POST'])
def login_page():
    login = request.form.get('login')
    password = request.form.get('password')

    #auth = request.authorization


    if login and password:
        user = User.query.filter_by(login=login).first()

        if  user and check_password_hash(user.password, password):
            token = jwt.encode({'public_id': user.id, 'exp': dt.utcnow() + timedelta(seconds=10)}, app.config['SECRET_KEY'])
            sys.argv.append({'token': token})


            #token = jwt.encode({'public_id':user.id,'exp':datetime.utcnow() + datetime.timedelta(minutes=30)},app.secret_key)
            login_user(user)

            next_page = request.args.get('next')

            return redirect(next_page)
            #return jsonify({'token': token.decode('UTF-8')})
        else:
            flash('Login or password is not correct')
    else:
        flash('Please fill login and password fields')

    #render_template('login.html')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
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
    app.run(debug=True)  #dev errors expected with debug mode
