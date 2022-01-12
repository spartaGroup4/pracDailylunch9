from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
# app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('localhost', 27017)
db = client.dbsparta


@app.route('/detail')
def detail():
    return render_template('detail.html')


@app.route('/detail', methods=['POST'])
def write_detail():
    # title_receive로 클라이언트가 준 title 가져오기
    title_receive = request.form['title_give']
    # content_receive로 클라이언트가 준 content 가져오기
    content_receive = request.form['content_give']
    # category_receive로 클라이언트가 준 category 가져오기
    category_receive = request.form['category_give']


    url_receive = request.form['url_give']

    # DB에 삽입할 detail 만들기
    doc = {
        'title': title_receive,
        'content': content_receive,
        'category': category_receive,
        'url': url_receive
    }
    # details에 detail 저장하기
    db.dbsparta.insert_one(doc)
    # 성공 여부 & 성공 메시지 반환
    return jsonify({'msg': ' 글이 성공적으로 작성되었습니다.'})




@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # 1. DB에서 detail 정보 모두 가져오기
        details = list(db.dbsparta.find({}, {'_id': False}))
        # 2. 성공 여부 & detail 목록 반환하기

        return render_template('index.html', details=details)
        # render_template를 통하여 index.html 에서 db 데이터 가져오기
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/api/comments', methods=['POST'])
def write_comment():
    # title_receive로 클라이언트가 준 title 가져오기
    nick_receive = request.form['nick_give']
    comment_receive = request.form['comment_give']

    # DB에 삽입할 review 만들기
    doc = {
        'nick': nick_receive,
        'comment': comment_receive
    }
    # reviews에 review 저장하기
    db.dailylunch.insert_one(doc)
    # 성공 여부 & 성공 메시지 반환
    return jsonify({'msg': '댓글이 성공적으로 작성되었습니다.'})


@app.route('/api/comments', methods=['GET'])
def read_comment():
    # 1. DB에서 리0뷰 정보 모두 가져오기
    lunches = list(db.dailylunch.find({}, {'_id': False}))
    # 2. 성공 여부 & 리뷰 목록 반환하기
    return jsonify({'all_lunches': lunches})


@app.route('/api/comment_delete', methods=['POST'])
def delete_comment():
    comment_receive = request.form['comment_give']
    db.dailylunch.delete_one({'comment': comment_receive})
    return jsonify({'msg': '삭제 완료!'})

@app.route('/')
def main():
    # DB에서 저장된 단어 찾아서 HTML에 나타내기
    words = list(db.dbsparta.find({}, {"_id": False}))
    return render_template("index.html", words=words)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)