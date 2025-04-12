from flask import Flask , render_template,request, redirect,session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///todo.db'
app.config["SQLALCHEMY_BINDS"]={
    "users" : "sqlite:///users.db"
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)
class TODO(db.Model):
    sno = db.Column(db.Integer , primary_key=True)
    title = db.Column(db.String(200) , nullable=False)
    desc = db.Column(db.String(500) , nullable = False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self)-> str:
        return f"{self.sno} - {self.title}"
class User(db.Model):
    __bind_key__ = 'users'  
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect('/login')  # redirect if not logged in

    if request.method == "POST":
        title = request.form["title"]
        desc = request.form['desc']
        todo = TODO(title=title, desc=desc)
        db.session.add(todo)
        db.session.commit()

    allTodo = TODO.query.all()
    return render_template("index.html", allTodo=allTodo)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):  # Secure password check
            session['user_id'] = user.id
            return redirect('/')
        else:
            return 'Invalid username or password'

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return 'Username already exists. Try logging in.'

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        return redirect('/')

    return render_template('register.html')

@app.route("/delete/<int:sno>")
def delete(sno):
    todo=TODO.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")
@app.route("/update/<int:sno>" , methods=["GET","POST"])
def update(sno):
    if request.method=="POST":
        title = request.form["title"]
        desc = request.form['desc']
        todo=TODO.query.filter_by(sno=sno).first()
        todo.title=title
        todo.desc = desc
        db.session.add(todo)
        db.session.commit()
        return redirect("/")
    todo=TODO.query.filter_by(sno=sno).first()
    return render_template("update.html" , todo=todo)

if __name__ =="__main__" :
    app.run(debug=True)
