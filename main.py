from flask import Flask,jsonify,request, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from functools import wraps
from environs import Env
import pdb

app= Flask(__name__)

env = Env()
env.read_env()

DB_URL = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=env("POSTGRES_USER"),pw=env("POSTGRES_PW"),url=env("URL"),db=env("POSTGRES_DB"))
#'postgresql://postgres:postgres@localhost/test'


app.config['SECRET_KEY']='secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning

db = SQLAlchemy(app)

class Users(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     public_id = db.Column(db.String(100))
     name = db.Column(db.String(50))
     password = db.Column(db.String(100))
     admin = db.Column(db.Boolean)

class Employees(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=False, nullable=True)
    salary = db.Column(db.Integer, unique=False, nullable=True)
    user_id = db.Column(db.Integer)

    def __init__(self, username, salary,user_id):
        self.username = username
        self.salary = salary
        self.user_id=user_id


    def __repr__(self):
        return '<Employees %r>' % self.username

# @app.route("/accounts",methods=["GET"])
# def getAccounts():
#         users=Employees.query.all()
#         results = [
#             {
#                 "name": user.username,
#                 "balance": user.salary,
#             } for user in users]
#         return jsonify(results)

# @app.route("/account", methods=["POST"])
# def addAccount():
#         # import pdb 
#         # pdb.set_trace()
#         name= request.json['name']
#         balance=request.json['balance']
#         # data={'name':name,'balance':balance}
#         # accounts.append(data)
#         user=Employees(username=name,salary=balance)
#         db.session.add(user)
#         db.session.commit()

#         return jsonify(name)

# @app.route("/account/<name>", methods=["DELETE"])
# def deleteAccounts(name):
#         user = Employees.query.filter_by(username=name).first()
#         db.session.delete(user)
#         db.session.commit()
#         return jsonify("Record deleted")

# @app.route("/accounts/<name>", methods=["PUT"])
# def updateAccounts(name):
#         user = Employees.query.filter_by(username=name).first()
#         user.username=request.json['name']
#         user.salary=request.json['balance']
#         db.session.add(user)
#         db.session.commit()
#         return jsonify("Record Updated")

@app.cli.command('resetdb')
def resetdb_command():
    """Destroys and creates the database + tables."""

    from sqlalchemy_utils import database_exists, create_database, drop_database
    if database_exists(DB_URL):
        print('Deleting database.')
        drop_database(DB_URL)
    if not database_exists(DB_URL):
        print('Creating database.')
        create_database(DB_URL)

    print('Creating tables.')
    db.create_all()
    print('Shiny!')


def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})

        try:
            data = jwt.decode(token,app.config['SECRET_KEY'],algorithms="HS256")
            current_user = Users.query.filter_by(public_id=data['public_id']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'token experied'})
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)
   return decorator

@app.route('/', methods=['GET'])
def index():
    return render_template('register.html')

@app.route('/register', methods=['GET', 'POST'])
def signup_user():  
        data = request.get_json()  

        hashed_password = generate_password_hash(data['password'], method='sha256')
        
        new_user = Users(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False) 
        db.session.add(new_user)  
        db.session.commit()    

        return jsonify({'message': 'registered successfully'})

@app.route('/login', methods=['GET', 'POST'])  
def login_user():
  pdb.set_trace()
  auth = request.authorization   

  if not auth or not auth.username or not auth.password:  
     return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})    

  user = Users.query.filter_by(name=auth.username).first()   
     
  if check_password_hash(user.password, auth.password):  
     token = jwt.encode({'public_id': user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'],algorithm="HS256")  
     return jsonify({'token' : token}) 

  return make_response('could not verify',  401, {'WWW.Authentication': 'Basic realm: "login required"'})

@app.route('/users', methods=['GET'])
def get_all_users():  
   
   users = Users.query.all() 

   result = []   

   for user in users:   
       user_data = {}   
       user_data['public_id'] = user.public_id  
       user_data['name'] = user.name 
       user_data['password'] = user.password
       user_data['admin'] = user.admin 
       
       result.append(user_data)   

   return jsonify({'users': result})

@app.route('/employee', methods=['POST'])
@token_required
def create_employee(current_user):
   
   data = request.get_json() 

   new_emp = Employees(username=data['name'], salary=data['salary'], user_id=current_user.id)  
   db.session.add(new_emp)   
   db.session.commit()   

   return jsonify({'message' : "New Employee Added for User "+ current_user.name })

@app.route('/employees', methods=['GET'])
@token_required
def get_employees(current_user):

    employees = Employees.query.filter_by(user_id=current_user.id).all()

    output = []
    for emp in employees:

           emp_data = {}
           emp_data['id'] = emp.id
           emp_data['username'] = emp.username
           emp_data['salary'] = emp.salary
           output.append(emp_data)

    return jsonify({'list_of_employees' : output})

@app.route('/employee/<employee_id>', methods=['DELETE'])
@token_required
def delete_employee(current_user, employee_id):  
    employee = Employees.query.filter_by(id=employee_id, user_id=current_user.id).first()
    if not employee:   
       return jsonify({'message': 'Employees does not exists'})   


    db.session.delete(employee)  
    db.session.commit()   

    return jsonify({'message': 'Employee deleted'})

@app.route('/employee/<employee_id>', methods=['PUT'])
@token_required
def update_employee(current_user,employee_id):
    employee=Employees.query.filter_by(id=employee_id,user_id=current_user.id).first()
    if not employee:   
       return jsonify({'message': 'Employees does not exists'})
    employee.username=request.json['username']
    employee.salary=request.json['salary']
    db.session.add(employee)
    db.session.commit()

    return jsonify({'message': "Record Updated"})



if __name__=="__main__":
    app.run()