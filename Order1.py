from flask import Flask
import flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_restful import Api
from flask import request
from flask import Flask,jsonify,json
import requests
import json
from datetime import datetime

app = Flask(__name__)
api = Api(app)

#catalogServer = 'http://catalog-server-1:4001'
#order_servers = ['http://orders-server-1:5002']

catalogServer = 'http://172.19.45.31:4001'
order_servers = ['http://172.19.45.31:5002']

@app.route('/orders', methods=['POST'])
def addNewOrder():
    body = request.get_json()
    id = body["id"]
    r = requests.get('{}/books/{}'.format(catalogServer, id))
    if r.status_code == 404:
        return abort(404, description="no books found") 

    response = r.json()
    quantity = response["quantity"]
    if quantity == 0 :
        return abort(400, description="out of stock") 

    newQuantity = quantity - 1
    response["quantity"] = newQuantity
     
    print("response = ")
    print(response)
    r2 = requests.put('{}/books/{}'.format(catalogServer , str(id)), json=(response))
    print("format(catalogServer , str(id)) = ")
    print(format(catalogServer , str(id)))
    if r2.status_code == 403: return abort(403, description="failed") 
  
    return jsonify({"title" : response["title"]})
 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port ='5001', threaded=True)
    #app.run(debug=False, port ='5001', threaded=True)
