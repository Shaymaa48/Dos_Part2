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


catalogServer = 'http://172.19.44.227:4002'
order_servers = ['http://172.19.45.31:5001']

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
    
    r2 = requests.put('{}/books/{}'.format(catalogServer , str(id)), json=(response))
    if r2.status_code == 403: return abort(403, description="failed") 
    elif r2.status_code == 204 :

        entry = {
        'id': int(id),
       
        'datetime': str(datetime.now())}
        
        with open("orders.json", "r") as file:
            data = json.load(file)
        data.append(entry)
        with open("orders.json", "w") as file:
            json.dump(data, file)

        for server in order_servers:
            requests.post('{}/db/orders'.format(server), json=(entry))
   
    return jsonify({"title" : response["title"]})
    
@app.route('/db/orders', methods=['POST'])
def addOrder():
    body = request.json
    try:
        with open("orders.json", "r") as file:
            data = json.load(file) 
        data.append(body)
        with open("orders.json", "w") as jsonFile:
            json.dump(data, jsonFile)
    except :
        return abort(400, description="empty fields") 
             
    return flask.Response(status=201)   

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port ='5002', threaded=True)
    #app.run(debug=False, port ='5002', threaded=True)
