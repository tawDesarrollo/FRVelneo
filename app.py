from flask import Flask, jsonify
from registerUser import registerNewUser
from getName import getUserName

app = Flask(__name__)

@app.route('/registerUser/<Session_ID>') 
def registerUser(Session_ID):
    return jsonify(registerNewUser(Session_ID))

@app.route('/getName/<Session_ID>')
def getNameOfUser(Session_ID):
    return jsonify(getUserName(Session_ID))

if __name__ == '__main__':
    app.run()
