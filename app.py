from flask import Flask, render_template, request, jsonify, redirect
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.j6ve73r.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

app = Flask(__name__)


@app.route('/')
def home():
    restaurant_list = list(db.michelin.find({}, {'_id': False}))
    return render_template('index.html', restaurant_list=restaurant_list)

@app.route('/login', methods=['GET'])
def getLogin():
    return render_template('login.html')

@app.route('/register', methods=['GET'])
def getRegister():
    return render_template('register.html')

@app.route('/<int:reviewId>', methods=["GET"])
def getOnerestaurant(reviewId):
    # print(type(reviewId), reviewId)

    review = list(db.michelin.find(
        {'reviewId':reviewId},
        {'_id': False}
    ))
    return jsonify({'review': review})

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/michelins', methods=['GET'])
def getAllrestaurant():
    restaurant_list = list(db.michelin.find({}, {'_id': False}))
    return jsonify({'restaurant_list': restaurant_list})



# @app.route('/remove')
# def tes1t():
#     db.michelin.drop()
#     return jsonify({'msg': 'remove success!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
