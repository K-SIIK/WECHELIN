from flask import Flask, render_template, request, jsonify, redirect
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient


# client = MongoClient('mongodb+srv://test:sparta@cluster0.j6ve73r.mongodb.net/Cluster0?retryWrites=true&w=majority')
# db = client.dbsparta

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/test')
def test():
    return render_template('test.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
