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
        # import pdb 
        # pdb.set_trace()
        name= request.json['name']
        balance=request.json['balance']
        data={'name':name,'balance':balance}
        accounts.append(data)

        return jsonify(data)

# Endpoint for deleting a record
@app.route("/account/<name>", methods=["DELETE"])
def deleteAccounts(name):
        acc=[account for account in accounts if account['name']==name]
        accounts.remove(acc[0])
        return jsonify(accounts)


if __name__=='__main__':
        app.run(port=8080)
