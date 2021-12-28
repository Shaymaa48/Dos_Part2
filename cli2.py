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
from itertools import cycle
import time
import argparse

import os
import sys
from typing import Type
from flask.json import jsonify
import requests
import json
from datetime import datetime
import time
import urllib
urllib.request
import urllib3
import http 
from itertools import cycle

app = Flask(__name__)
api = Api(app)

divider = "\n-----------------------------------------------\n"
exit = "/exit"
help = "/help"
search = "/search"
info = "/info"
purchase = "/purchase"



# SERVER_POOL_CATALOG = ['http://catalog-server-2:4002', 'http://catalog-server-1:4001']
# SERVER_POOL_ORDER = ['http://orders-server-1:6001', 'http://orders-server-2:6002']

SERVER_POOL_CATALOG = ["http://172.19.45.31:4001","http://172.19.44.227:4002"]
SERVER_POOL_ORDER = ["http://172.19.44.227:5001" , "http://172.19.45.31:5002"]

ITER_CATALOG = cycle(SERVER_POOL_CATALOG)
ITER_ORDER = cycle(SERVER_POOL_ORDER)

def round_robin(iter):
    return next(iter)

divider = "\n-----------------------------------------------\n"

@app.route('/info/<id>', methods=['GET'])
def getBookById(id):
    time_before = float(time.time())
    now1 = time.ctime(time_before)
    print("Time_info_request: {0}".format(now1))
    
    
    book = bookFoundInCache(id)
    if book is not None :
        time_after = float(time.time())
        now = time.ctime(time_after)
        print("Time_info_response: {0}".format(now))
        time_taken = time_after - time_before
        print ("Latency: ", time_taken)   
        return formatInfoResponse(book)

    server = round_robin(ITER_CATALOG)
    r = requests.get('{}/books/{}'.format(server, id))
    if r.status_code == 404:
        return "invalid book number" 

    if r.status_code == 200:
        response = r.json()
        addBookToCache(response)
        time_after = float(time.time())
        now = time.ctime(time_after)
        print("Time_info_response: {0}".format(now))
        print("Response Time: ", r.elapsed.total_seconds())
        time_taken = time_after - time_before
        print ("Latency: ", time_taken)   
        return formatInfoResponse(response)
    

    else : return "ERROR try again later"

@app.route('/search/<topic>', methods=['GET'])
def getBooksByTopic(topic):
    time_before = float(time.time())
    now1 = time.ctime(time_before)
    print("Time_search_request: {0}".format(now1))
    
    
    topicsList = topicFoundInCache(topic)
    if topicsList is not None :
        time_after = float(time.time())
        now = time.ctime(time_after)
        print("Time_info_response: {0}".format(now))
        time_taken = time_after - time_before
        print ("Latency: ", time_taken)  
         
        return formatTopicResponse(topicsList)

    server = round_robin(ITER_CATALOG)
    r = requests.get('{}/books?topic={}'.format(server, topic))
    if r.status_code == 404:
        return "  no books found with this topic" 
    if r.status_code == 200:
        response = r.json()
        booksList = []
        for book in response:
            addBookToCache(book)
            booksList.append(str(book["id"]))   
        addTopicToCache(topic, booksList) 
        time_after = float(time.time())
        now = time.ctime(time_after)
        print("Time_search_response: {0}".format(now))
        print("Response Time: ", r.elapsed.total_seconds())
        time_taken = time_after - time_before
        print ("Latency: ", time_taken)
        
        return formatTopicResponse(response)

    else : return "ERROR try again later"    


@app.route('/purchase/<id>', methods=['POST'])
def updateBookQuantity(id):
   
    
    time_before = float(time.time())
    now1 = time.ctime(time_before)
    print("Time_purchase_request: {0}".format(now1))
    server = round_robin(ITER_ORDER)

    #r = requests.post('{}/orders'.format(server))
    #r = requests.post('http://localhost:3000/orders/{}'.format(id))
    print("id ===" + id)
    r = requests.post('{}/orders'.format(server),json=({"id": int(id)}))
 
    if r.status_code == 404:
        return "No Book found, Invalid Id"
    if r.status_code == 400:
        return "Out of stock"
    if r.status_code == 200:
        response = r.json()
        time_after = float(time.time())
        now = time.ctime(time_after)
        print("Time_purchase_response: {0}".format(now))
        print("Response Time: ", r.elapsed.total_seconds())
        time_taken = time_after - time_before
        print ("Latency: ", time_taken)
        return "Bought Book '" + response["title"]+"'"
    else : return r.status_code 
        

@app.route('/invalidate', methods=['POST'])
def removeBookFromCache():
    book = request.json
    with open("cache.json", "r") as file:
        data = json.load(file)

    data["books"].pop(str(book["id"]), None)
    data["topics"].pop(book["topic"], None)
    
    with open("cache.json", "w") as file:
        json.dump(data, file)

    return flask.Response(status=200) 

def bookFoundInCache(id):
    
    with open("cache.json", "r") as file:
        data = json.load(file) 

    if id in data["books"]:
        return data["books"][id]

    return None        

def topicFoundInCache(topic):
    booksList = []
    
    with open("cache.json", "r") as file:
        data = json.load(file) 
    if topic in data['topics']:
        for book in data['topics'][topic]: 
            booksList.append(data['books'][book])
        return booksList

    return None  
    
def addBookToCache(book):   

    with open("cache.json", "r") as file:
        data = json.load(file)

    if book["id"] in data["books"]:
        return

    data["books"][book["id"]] = book

    with open("cache.json", "w") as file:
        json.dump(data, file)

def addTopicToCache(topic, books):   
    with open("cache.json", "r") as file:
            data = json.load(file)

    data["topics"][topic] = books

    with open("cache.json", "w") as file:
        json.dump(data, file)  

def formatInfoResponse(response):
    res = divider
    res +=  "id      : "+str(response["id"]) + "\n" 
    res +=  "title   : "+response["title"] + "\n" 
    res +=  "price   : "+str(response["price"])+ "\n" 
    res +=  "quantity: "+str(response["quantity"]) 
    res += divider    
    return res

def formatTopicResponse(response):
    res = divider
    for book in response:
        res += "id    : "+str(book["id"]) + "\n" 
        res += "title : "+book["title"] 
        res += divider
    return res
     

commandslist = ["search {topic}", "info {item_num}", "purchase {item_num}"]

print("\n Welcome to Bazar.com! \n")
print("\n What would you like to do? (use /help for commands list) ")
print("(use /exit to exit) \n")

Userinput = ""
while (True):
    Userinput = input("> ")
    command = Userinput.split(" ", 1)
    if Userinput == exit:
        break
    elif Userinput == help:
        print("\n /search (topic)\n")
        print(" /info (item_id)\n")
        print(" /purchase (item_id)\n")
    elif len(command) < 2:
        print("  invalid command")
    else:
        if command[0] == search:
            print(getBooksByTopic(command[1]))

        elif (command[0] == info):
            print(getBookById(command[1]))

        elif (command[0] == purchase) :
           
            print(updateBookQuantity(command[1]))
        else:
            print("  invalid command")
    

print("Hope You Enjoyed Your Shopping!")


if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0', threaded=True)
    app.run(debug=False,host='0.0.0.0', port ='3000', threaded=True)
