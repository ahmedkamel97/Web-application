#Importing All the needed libraries
import os #To handle files path
from flask import Flask, render_template, redirect, request, g, session #Main Flask
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required #To create the Login
from flask_sqlalchemy import SQLAlchemy #SQL Alchemy to create the database

#Initial Configurations
files_path = os.path.dirname(os.path.abspath(__file__)) #Setting the path of the main directory
database_main_file = "sqlite:///{}".format(os.path.join(files_path, "primary.db")) #The path of the main database
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_main_file
app.secret_key = "A06748581"
login = LoginManager()
login.init_app(app)
login.login_view = 'login'
db = SQLAlchemy(app)

#Creating the primary database
class Task(db.Model): # A table to store all the tasks with a unique id as an identifier
    __tablename__ = 'Task'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    status = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    def __repr__(self):
        return "<Title: {}>".format(self.title)

class User(UserMixin, db.Model): # A table to store users data
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200))
    password = db.Column(db.String(200))
    task_id = db.relationship('Task', backref='user', lazy='dynamic') #Creating the relation between the two databases
    def __repr__(self):
        return "<Username: {}>".format(self.username)

# Generating the database with the two tables
db.create_all()
db.session.commit()


#The primary functions

"""
This function redirects users to the Login page 
"""
@app.route('/', methods=['GET', 'POST'])
def welcome():
    return redirect('login')

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

"""
This the primary function responsible for registering new users 
This function assures that the password has at least 8 figures 
This function returns an error if the password does not meet the requirements
This function returns an error if the password do not match
This function returns an error if the username already exists in the database   
"""
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is not None:
            error = 'This username already exists! please choose a new username'
            return render_template('register.html', error=error)
        if len(request.form['password']) < 8:
            error = 'Your password should be at least 8 symbols long. Please, try again.'
            return render_template('register.html', error=error)
        if request.form['password'] != request.form['repeat']:
            error = 'Passwords do not match. Please, try again.'
            return render_template('register.html', error=error)

        new_user = User(username=request.form['username'], password=request.form['password'])
        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")
    elif request.method == 'GET':
        return render_template('register.html')


"""
This function is responsible for logging users in to their personal kanban board 
This function validates users credentials, if the user is registered it redirects to the Kanban board
If the user is not registered it displays an error that the user is not registered
"""
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username'], password=request.form['password']).first()
        if user is None:
            error = 'The password or the username you  entered is not correct!'
            return render_template('login.html', error=error)
        login_user(user)
        return redirect("/main")
    elif request.method == 'GET':
        return render_template('login.html')

"""
This function is responsible for logging users out
"""
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('logged_in', None)
    return redirect('login')

"""
This is the primary function responsible for displaying the tasks 
This function does not allow duplicate tasks to exist 

"""
@app.route('/main', methods=["GET", "POST"])
@login_required
def home():
    g.user = current_user
    tasks = None
    error = None
    if request.form:
        try:
            if request.form.get("title") in [task.title for task in Task.query.all()]:
                error = "This task already exists."
            else:
                task = Task(id = 1, title=request.form.get("title"), status=request.form.get("status"), user_id = g.user.id)
                tasks = Task.query.all()
                db.session.add(task)
                db.session.commit()
        except Exception as e:
            print("Failed to add task")
            print(e)
    tasks = Task.query.filter_by(user_id=g.user.id).all()
    todo = Task.query.filter_by(status='todo',user_id=g.user.id).all()
    doing = Task.query.filter_by(status='doing',user_id=g.user.id).all()
    done = Task.query.filter_by(status='done',user_id=g.user.id).all()
    return render_template("index.html", error=error, tasks=tasks, todo=todo, doing=doing, done=done, myuser=current_user)

@app.route("/update", methods=["POST"])
def update():
    try:
        newstatus = request.form.get("newstatus")
        name = request.form.get("name")
        task = Task.query.filter_by(title=name).first()
        task.status = newstatus
        db.session.commit()
    except Exception as e:
        print("Couldn't update task status")
        print(e)
    return redirect("/main")

@app.route("/delete", methods=["POST"])
def delete():
    title = request.form.get("title")
    task = Task.query.filter_by(title=title).first()
    db.session.delete(task)
    db.session.commit()
    return redirect("/main")


#Running the application
if __name__ == "__main__":
    app.run(debug=True)
