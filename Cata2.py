from flask import Flask
import flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_restful import Api
from flask import request
from flask import Flask,jsonify,json
import json
import requests

app = Flask(__name__)
api = Api(app)

#cacheServer = 'http://FrontendCache-server:3000'
#catalog_servers = ['http://catalog-server-2:4002']

cacheServer = "http://192.168.1.111:3000"
catalog_servers = ['http://192.168.1.111:4001']

 
@app.route('/books/<id>', methods=['GET'])
def getBookById(id):

    f = open('books.json',) 
    data = json.load(f) 

    for book in data['books']: 
        if book['id'] == int(id) :
            return jsonify(book)
    f.close()
    abort(404)

@app.route('/books', methods=['GET'])
def getBooksByTopic():
    topic = request.args.get('topic')
    f = open('books.json',) 
    data = json.load(f) 
    booksList = []
    for book in data['books']: 
        if book['topic'] == topic :
            booksList.append(book)
            
    f.close()

    if len(booksList) == 0 :
        abort(404)

    return jsonify(booksList)

@app.route('/books/<id>', methods=['PUT'])
def updateBookQuantity(id):

    body = request.json
    newQuantity = body["quantity"]

    requests.post('{}/invalidate'.format(cacheServer), json=(body))

    f = open('books.json','r+') 
    data = json.load(f) 
    for book in data['books']: 
        if book['id'] == int(id) :
            if (book['quantity'] < 1) or (newQuantity < 0) : 
                return abort(403) 
            book['title'] = body["title"]
            book['topic'] = body["topic"]
            book['quantity'] = newQuantity
            book['price'] = body["price"]
    f.close()

    with open("books.json", "w") as jsonFile:
        json.dump(data, jsonFile)

    for server in catalog_servers:
        requests.put('{}/db/books/{}'.format(server,id), json=(body))

    return flask.Response(status=204)



@app.route('/db/books/<id>', methods=['PUT'])
def updateBook(id):

    body = request.json

    f = open('books.json','r+') 
    data = json.load(f) 
    for book in data['books']: 
        if book['id'] == int(id) :
            book['title'] = body["title"]
            book['topic'] = body["topic"]
            book['quantity'] = body["quantity"]
            book['price'] = body["price"]
    f.close()

    with open("books.json", "w") as jsonFile:
        json.dump(data, jsonFile)

    return flask.Response(status=204)

 

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port ='4002', threaded=True)
    #app.run(debug=False, port ='4002', threaded=True)
