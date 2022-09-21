import hashlib

import jwt
from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import datetime
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.j6ve73r.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

app = Flask(__name__)

# JWT 토큰 암호화에 사용될 비밀키
SECRET_KEY = 'WECHELIN'


@app.route('/')
def home():
    token_receive = request.cookies.get('mtoken')
    print('GET / \t\t\t> ', token_receive)

    restaurant_list = list(db.michelin.find({}, {'_id': False}).sort('star', -1))
    # print(restaurant_list)

    userId = "비회원"

    if (token_receive is not None):
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.user.find_one({"id": payload["id"]})

            userId = user_info['id']
            # print(user_info['id'])
            return render_template('index.html', restaurant_list=restaurant_list, userId=userId)
        except jwt.ExpiredSignatureError:
            return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))
    return render_template('index.html', restaurant_list=restaurant_list, userId=userId)

@app.route('/login', methods=['GET'])
def getLogin():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def postLogin():
    id = request.form['id']
    pw = request.form['pw']

    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

    findUser = db.user.find_one({'id': id, 'pw': pw_hash})

    if findUser == None:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

    payload = {
        'id': id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 30)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

    print('POST /login \t> ', token)

    return jsonify({'result': 'success', 'token': token})

@app.route('/register', methods=['GET'])
def getRegister():
    return render_template('register.html')


@app.route('/register/chkDup', methods=['POST'])
def chkDupId():
    id = request.form['id']
    isExist = bool(db.user.find_one({"id": id}))

    return jsonify({'result': 'success', 'isExist': isExist})

@app.route('/register', methods=['POST'])
def postRegister():
    # db.user.drop()

    id = request.form['id']
    pw = request.form['pw1']

    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

    doc = {
        "id": id,  # 아이디
        "pw": pw_hash,  # 비밀번호
        "profile_pic": "",  # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지
        "profile_info": ""  # 프로필 한 마디
    }
    db.user.insert_one(doc)

    return jsonify({'result': 'success'})
    # return redirect('/login')

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

@app.route('/detail', methods=['GET'])
def getDetail():
    return render_template('detail.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
