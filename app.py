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
            return redirect(url_for("getLogin", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("getLogin", msg="로그인 정보가 존재하지 않습니다."))

    return render_template('index.html', restaurant_list=restaurant_list, userId=userId)


@app.route('/login', methods=['GET'])
def getLogin():

    msg = request.args.get('msg')

    timeout = "로그인 시간이 만료되었습니다."
    noExisted = "로그인 정보가 존재하지 않습니다."

    if(msg != None):
        if(timeout == msg):
            return render_template('login.html', status=True, w = 't')
        elif(noExisted == msg):
            return render_template('login.html', status=True, w = 'n')

    return render_template('login.html', status=False)


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
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60)
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

@app.route('/<int:reviewId>')
def getDetailComment(reviewId):
    detail = db.michelin.find_one({'reviewId': reviewId})
    comment_list = list(db.comment.find({'reviewId': reviewId}, {'_id': False}))

    return render_template('detail.html', detail=detail, comment_list=comment_list)


@app.route('/<int:reviewId>/post', methods=['POST'])
def postComment(reviewId):
    comment_recieve = request.form['comment_give']

    comment_list = list(db.comment.find({'reviewId': reviewId}))
    cmtId = len(comment_list) + 1

    # token_recieve = request.cookies.get('mtoken')
    # paylode = jwt.decode(token_recieve, SECRET_KEY, algorithms=['HS256'])
    # user_info = db.user.find_one({'id': paylode['id']})

    # userId = user_info['id']

    doc = {
        'reviewId': reviewId,
        'cmtId': cmtId,
        'userId': userId,
        'comment': comment_recieve
    }
    db.comment.insert_one(doc)
    return jsonify({'msg': 'posted!'})


@app.route('/<int:reviewId>/delete/<int:cmtId>', methods=['DELETE'])
def deleteComment(reviewId, cmtId):
    # cmtId : 댓글 번호
    db.comment.delete_one({'reviewId': reviewId, 'cmtId': cmtId})

    delete_info = list(db.comment.find({'reviewId': reviewId, 'cmtId': {'&gt': cmtId}}))
    cnt = len(delete_info)

    if cnt != 0:
        for i in range(cmtId + 1, cmtId + cnt + 1):
            db.comment.update_one({'reviewId': reviewId, "cmtId": i}, {'&set': {"cmtId": i - 1}})

    return jsonify({'msg': '삭제 완료'})


# @app.route('/<int:reviewId>/edited', methods=['POST'])
# def editedComment(reviewId):


@app.route('/<int:reviewId>/edit', methods=['GET'])
def editComment(reviewId):
    num_recieve = int(requests.form['num_give'])
    editData = db.comment.find_one({'reviewId': reviewId, 'num': num_recieve})
    return jsonify({'editData': editData})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
