from flask import Flask,render_template,url_for,request,redirect
from flask_sqlalchemy import SQLAlchemy  #if cant import flask_sqlalchemy:
                                                                        # try configurate VENV again
                                                                        # make sure that U use right interpreter

from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///articles_adjustment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  #if you see notice 'SQLALCHEMY_TRACK_MODIFICATIONS'--> add this config,it is not important thought
db = SQLAlchemy(app)


class Articles(db.Model):
        id = db.Column(db.Integer,primary_key = True)
        title = db.Column(db.String(100),nullable = False)
        intro = db.Column(db.String(300),nullable = False)
        text = db.Column(db.Text,nullable = False)
        date = db.Column(db.DateTime, default = datetime.utcnow)

        def __repr__(self):
            return '<Articles %r>' % self.id


@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/posts')
def posts():

    articles = Articles.query.order_by(Articles.date.desc()).all()
    return render_template("posts.html", articles = articles)

@app.route('/posts/<int:id>')
def posts_text(id):

    article = Articles.query.get(id)
    return render_template("post_text.html", article = article)


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
def create_article():
    if request.method == "POST":
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

if __name__ == "__main__":
    app.run(debug=True)  #dev errors expected with debug mode
