import hashlib

import jwt
from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import datetime, time
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

    access = "로그인 후 이용 가능합니다."
    timeout = "로그인 시간이 만료되었습니다."
    noExisted = "로그인 정보가 존재하지 않습니다."

    if (msg != None):
        if (timeout == msg):
            return render_template('login.html', status=True, w='t')
        elif (noExisted == msg):
            return render_template('login.html', status=True, w='n')
        elif (access == msg):
            return render_template('login.html', status=True, w='a')

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

@app.route('/mypage', methods=['GET'])
def getMypage():
    token_receive = request.cookies.get('mtoken')
    # print('getMypage.token_receive > ', token_receive)
    if (token_receive is not None):
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.user.find_one({"id": payload["id"]})

            return render_template('mypage.html', userId=user_info['id'])
        except jwt.ExpiredSignatureError:
            return redirect(url_for("getLogin"))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("getLogin"))


@app.route('/mypage/getComment', methods=['GET'])
def getMyComment():
    token_receive = request.cookies.get('mtoken')
    # print('getMypage.token_receive > ', token_receive)
    if (token_receive is not None):
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.user.find_one({"id": payload["id"]})

            comments = list(db.comment.find({'userId': user_info['id']}, {'_id': False}))
            # print(comments)

            return jsonify(status='success', comments=comments)
        except jwt.ExpiredSignatureError:
            return redirect(url_for("getLogin", msg="로그인 시간이 만료되었습니다."))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("getLogin", msg="로그인 정보가 존재하지 않습니다."))

    return jsonify(status='fail')


@app.route('/<int:reviewId>')
def getDetailComment(reviewId):
    token_receive = request.cookies.get('mtoken')

    if (token_receive is None):
        return redirect(url_for("getLogin", msg="로그인 후 이용 가능합니다."))

    detail = db.michelin.find_one({'reviewId': reviewId})
    comment_list = list(db.comment.find({'reviewId': reviewId}, {'_id': False}))

    token_recvieve = request.cookies.get('mtoken')

    userId = '비회원'

    if (token_recvieve is not None):
        try:
            paylode = jwt.decode(token_recvieve, SECRET_KEY)
            user_info = db.user.find_one({'id': paylode['id']})

            userId = user_info['id']
            return render_template('detail.html', detail=detail, comment_list=comment_list, userId=userId)
        except jwt.ExpiredSignatureError:
            return redirect(url_for('getLogin', msg='로그인 시간이 만료 되었습니다.'))
        except jwt.exceptions.DecodeError:
            return redirect(url_for('getLogin', msg='로그인 정보가 존재하지 않습니다.'))
    return render_template('detail.html', detail=detail, comment_list=comment_list, userId=userId)

@app.route('/<int:reviewId>/post', methods=['POST'])
def postComment(reviewId):
    token_receive = request.cookies.get('mtoken')

    if (token_receive is None):
        return redirect(url_for("getLogin", msg="로그인 후 이용 가능합니다."))

    comment_receive = request.form['comment_give']

    try:
        paylode = jwt.decode(token_receive, SECRET_KEY)
        user_info = db.user.find_one({'id': paylode['id']})
        cmt = list(db.comment.find({}, {'_id': False}).sort('cmtId', -1).limit(1))

        if(len(cmt) == 0):
            cmt = 0
        else:
            cmt = cmt[0]['cmtId']

        doc = {
            'reviewId': reviewId,
            'cmtId': cmt + 1,
            'userId': user_info['id'],
            'comment': comment_receive,
            'date': datetime.datetime.utcnow()
        }
        db.comment.insert_one(doc)

        return jsonify({'msg': '댓글 등록이 완료되었습니다.'})
    except jwt.ExpiredSignatureError:
        return redirect(url_for('getLogin', msg='로그인 시간이 만료 되었습니다.'))
    except jwt.exceptions.DecodeError:
        return redirect(url_for('getLogin', msg='로그인 정보가 존재하지 않습니다.'))


@app.route('/<int:reviewId>/delete/<int:cmtId>', methods=['DELETE'])
def deleteComment(reviewId, cmtId):
    token_receive = request.cookies.get('mtoken')

    if (token_receive is None):
        return redirect(url_for("getLogin", msg="로그인 후 이용 가능합니다."))

    try:
        paylode = jwt.decode(token_receive, SECRET_KEY)
        user_info = db.user.find_one({'id': paylode['id']})
        comment_info = db.comment.find_one({'cmtId': cmtId})

        if(user_info['id'] == comment_info['userId']):
            db.comment.delete_one({'reviewId': reviewId, 'cmtId': cmtId})
            return jsonify({'msg': '삭제가 완료되었습니다.'})
        else:
            return jsonify({'msg': '작성자가 아닙니다.'})

    except jwt.ExpiredSignatureError:
        return redirect(url_for('getLogin', msg='로그인 시간이 만료 되었습니다.'))
    except jwt.exceptions.DecodeError:
        return redirect(url_for('getLogin', msg='로그인 정보가 존재하지 않습니다.'))


@app.route('/<int:reviewId>/edit/<int:cmtId>', methods=['GET'])
def editComment(reviewId, cmtId):
    editData = db.comment.find_one({'reviewId': reviewId, 'cmtId': cmtId}, {'_id': False})
    return jsonify(editData)


@app.route('/<int:reviewId>/resave/<int:cmtId>', methods=['POST'])
def editedComment(reviewId, cmtId):
    comment_recieve = request.form['comment_give']
    db.comment.update_one({'reviewId': reviewId, 'cmtId': cmtId}, {'$set': {'comment': comment_recieve}})
    return jsonify({'msg': '수정 완료'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
