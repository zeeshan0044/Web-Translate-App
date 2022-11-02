"""     English to Bengali Web Translate App

    Libary: 1) pip install Authlib Flask
            2) pip install requests
            3) pip install googletrans==3.1.0a0
 """

from flask_sqlalchemy import SQLAlchemy
from googletrans import Translator
from datetime import datetime
from flask import Flask, session, redirect,url_for,request,render_template
from authlib.integrations.flask_client import OAuth

loginApp = Flask(__name__)
loginApp.secret_key = 'random secret'
loginApp.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///dictionary.db"
loginApp.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(loginApp)
wordBook = {}

# oauth config
oauth = OAuth(loginApp)
google = oauth.register(
    name='google',
    client_id='171550099525-t1mqtheggqsonehn4615bd2pgfpsn1gq.apps.googleusercontent.com',
    client_secret='jrEKcOkZcSlkY_LzUZebOoGT',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    acess_token_params = None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid profile email'},
)

@loginApp.route("/", methods=['GET','POST'])
def home():
   return render_template("loginPage.html")
    
@loginApp.route('/myDict',methods=['GET','POST'])
def myDic():  
    if request.method =='POST':
        while len(wordBook):
            wordBook.popitem()
            continue
        print("Post is done")
        eng = request.form['EngWord']
        translator = Translator()
        transWord = translator.translate(eng,dest='bn',src='en')
        ben = transWord.text
        wordBook[eng] = ben
        print(f"Bengali to Eenglish: {eng} {ben}")
        return redirect("/translate")               # If the any post operation is happend then this html will show
    myDict = WordDictionary()
    allWord = myDict.query.all()
    return render_template("home.html",myDict=allWord)             # When we are in a root page we this function is wxwcuted

@loginApp.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@loginApp.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()  # Access token from google (needed to get user info)
    resp = google.get('userinfo')
    user_info = resp.json()
    session['email'] = user_info['email']
    return redirect('/myDict')

@loginApp.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')


# NOTE: Translator and Storage Part
class WordDictionary(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    eng = db.Column(db.String(100),nullable=False)
    ben = db.Column(db.String(200),nullable=False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"{self.sno} - {self.eng} - {self.ben}"
     
@loginApp.route("/translate")
def wordTranslate():
    return render_template("translate.html",word=wordBook)

@loginApp.route("/addDict",methods=['GET','POST'])
def wordAdd():
    english, bengali = list(wordBook.items())[0]
    myDict = WordDictionary(eng=english,ben=bengali)
    db.session.add(myDict)
    db.session.commit()
    
    allWord = myDict.query.all()
    print(allWord)
    print(f"eng = {english} and bengali= {bengali}")

    return render_template('home.html', myDict=allWord)
    
@loginApp.route("/delete/<int:sno>")
def delete(sno):
    word = WordDictionary.query.filter_by(sno=sno).first()
    print("In delet methods: ",word)
    db.session.delete(word)
    db.session.commit()
    return redirect('/myDict')

@loginApp.route("/about")   
def about():
    return render_template("about.html")


if __name__ == "__main__":
    loginApp.run(debug=True)
