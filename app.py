from flask import Flask,render_template,url_for
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
    return render_template('about.html')\


@app.route('/create-article')
def add():
    return render_template('create-article.html')



@app.route('/user/<string:name>/<int:id>')
def user(name, id):
    return "User  "+name+'--'+str(id)

if __name__ == "__main__":
    app.run(debug=True)  #dev errors expected
