from flask import Flask,jsonify,request

app=Flask(__name__)

accounts=[
        {'name':"Billy",'balance':450.0},
        {'name':"Kelly",'balance':250.0}
        ]

@app.route("/accounts",methods=["GET"])
def getAccounts():
        return jsonify(accounts)

@app.route("/accounts/<id>",methods=["GET"])
def getAccount(id):
    id=int(id)-1
    return jsonify(accounts[id])

@app.route("/account", methods=["POST"])
def addAccount():
        name= request.json['name']
        balance=request.json['balance']
        data={'name':name,'balance':balance}
        accounts.append(data)

        return jsonify(data)

if __name__=='__main__':
        app.run(port=8080)
