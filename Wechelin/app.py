from flask import Flask, render_template, request, jsonify, redirect
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.wzrslas.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/michelins', methods=['GET'])
def get_restaurant():
    restaurant_list = list(db.michelin.find({}, {'_id': False}))
    return jsonify({'restaurant_list': restaurant_list})


@app.route('/test')
def test():
    return render_template('test.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
