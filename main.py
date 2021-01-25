from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy

app= Flask(__name__)
#DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=False, nullable=True)
    salary = db.Column(db.Integer, unique=False, nullable=True)

    def __init__(self, username, salary):
        self.username = username
        self.salary = salary


    def __repr__(self):
        return '<User %r>' % self.username

@app.route("/accounts",methods=["GET"])
def getAccounts():
        users=User.query.all()
        results = [
            {
                "name": user.username,
                "balance": user.salary,
            } for user in users]
        return jsonify(results)

@app.route("/account", methods=["POST"])
def addAccount():
        # import pdb 
        # pdb.set_trace()
        name= request.json['name']
        balance=request.json['balance']
        # data={'name':name,'balance':balance}
        # accounts.append(data)
        user=User(username=name,salary=balance)
        db.session.add(user)
        db.session.commit()

        return jsonify(name)

@app.route("/account/<name>", methods=["DELETE"])
def deleteAccounts(name):
        user = User.query.filter_by(username=name).first()
        db.session.delete(user)
        db.session.commit()
        return jsonify("Record deleted")

@app.route("/accounts/<name>", methods=["PUT"])
def updateAccounts(name):
        user = User.query.filter_by(username=name).first()
        user.username=request.json['name']
        user.salary=request.json['balance']
        db.session.add(user)
        db.session.commit()
        return jsonify("Record Updated")

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


if __name__=="__main__":
    app.run()