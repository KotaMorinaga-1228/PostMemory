import sqlite3
import datetime
import time
from flask import Flask,render_template,request,session,redirect,url_for, g
from models.models import User
from models.database import db_session
from datetime import datetime
from hashlib import sha256
import random, string
import pyknp
import bleach

def randomname(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

def get_db():
    if 'db' not in g:
        # データベースをオープンしてFlaskのグローバル変数に保存
        g.db = sqlite3.connect('models/archives.db')
    return g.db

app = Flask(__name__)
app.secret_key = "g8wkf0pvje6m2unhgt3j"
dt_now = datetime.now()


@app.route("/")
def top():
    return render_template('top.html')

@app.route("/index", methods = ["GET" , "POST"])
def index():
    if "user_name" in session:
        if request.method == 'POST':
            user_name = session["user_name"]
            user = User.query.filter_by(user_name=user_name).first()
            user_id = user.id
            body = request.form["body"]
            URL_id = request.form["URL_id"]
            body=str(body)
            date = dt_now
            secret = ''

            where = {}
            order=0
            def remove_str(s, start, end):
                return s[:start] + s[end + 1:]
            while True:
                st=body.find('<span class="highlighted">',order)
                ed=body.find('</span>',order)
                cf = body.find('<span class="highlighted">',st+26,ed)
                if st == -1:
                    break
                else:
                    if cf != -1:
                        body=remove_str(body,cf,cf+25)
                        ed=body.find('</span>',order)
                        body=remove_str(body,ed,ed+6)
                    else:
                        where[st+26] = str(ed-1)
                        order=ed+7

            for key,value in where.items():
                key = str(key)
                value = str(value)
                if secret == '':
                    secret = key + ':' + value
                else:
                    secret += ','+ key + ':'+ value

            con = get_db()
        
            sql = "INSERT INTO archives (user_id, URL_id, body, secret, date) VALUES (?, ?, ?, ?, ?)"
            con.execute(sql, (user_id, URL_id, body, secret, date))
            con.commit()
            con.close()
            time.sleep(2)
            return redirect(url_for('complete'))
        else:
            con = get_db()
            cur = con.cursor()
            sql = "SELECT COUNT(*) FROM URLs"
            cur.execute(sql)
            length = list(cur.fetchone())
            id = random.randint(1,int(length[0]))
            sql = "SELECT URL FROM URLs WHERE id = ?"
            cur.execute(sql, (id,))
            link = list(cur.fetchone())
            cur.close()
            con.close()
            return render_template('post.html',link=link[0], URL_id = id)
    else:
        return redirect(url_for("top",status="logout"))

@app.route("/parse", methods = ["POST"])
def parse():
    if "user_name" in session:
        link = request.form["link"]
        URL_id = request.form["URL_id"]
        origin_body =request.form["origin-body"]
        body=''
        knp = pyknp.KNP()
        # 文字列を解析
        result = knp.parse(origin_body)
        # 基本句を格納するリスト
        body=""
        # 解析結果から基本句を取得してリストに格納
        for mrph in result.mrph_list():
            midasi = mrph.midasi
            if "固有キー" in mrph.fstring:
                # 基本句が固有表現の場合、tagを挿入
                body += '<span class="highlighted">'+midasi+'</span>'
            else:
                body+=midasi

        allowed_tags = ['span']  # 許可するタグ
        allowed_attributes = {'span': ['class']}  # spanタグに許可する属性
        parsed_body = bleach.clean(body, tags=allowed_tags, attributes=allowed_attributes)

        return render_template('post.html', parsed_body=parsed_body, link=link, URL_id= URL_id)
    else:
        return redirect(url_for("login"))

@app.route("/complete")
def complete():
    return render_template("complete.html")

@app.route("/items")
def items():
  if "user_name" in session:
    user_name = session["user_name"]
    user = User.query.filter_by(user_name=user_name).first()
    user_id = user.id
    con = get_db()
    cur = con.cursor()
    sql="SELECT archives.id, URLs.URL FROM archives INNER JOIN URLs ON archives.URL_id = URLs.id where archives.user_id = ?"
    cur.execute(sql,(user_id,))
    archives_data = cur.fetchall()
    cur.close()
    con.close()
    return render_template('items.html', items=archives_data, user_name=user_name)
  else:
    return redirect(url_for("login"))

@app.route("/item")
def item():
    if "user_name" in session:
        archive_id = request.args.get('id', '')
        con = get_db()
        cur = con.cursor()
        sql="SELECT user_id FROM archives WHERE id = ?"
        cur.execute(sql,(archive_id,))
        userid=cur.fetchone()
        user_name = session["user_name"]
        user = User.query.filter_by(user_name=user_name).first()
        user_id = user.id
        if int(userid[0]) == user_id:
            sql="SELECT archives.id, archives.body, URLs.URL FROM archives INNER JOIN URLs ON archives.URL_id = URLs.id where archives.id = ?"
            cur.execute(sql,(archive_id,))
            data=cur.fetchone()
            cur.close()
            con.close()
            return render_template("item.html",data=data)
        else:
            cur.close()
            con.close()
            return redirect(url_for("items"))

    else:
        return redirect(url_for("top",status="logout"))
    
@app.route("/modify",methods=["POST"])
def modify():
    if "user_name" in session:
        body = request.form["body"]
        id = request.form["archives_id"]
        body=str(body)
        date = dt_now
        secret = ''

        where = {}
        order=0
        def remove_str(s, start, end):
            return s[:start] + s[end + 1:]
        while True:
            st=body.find('<span class="highlighted">',order)
            ed=body.find('</span>',order)
            cf = body.find('<span class="highlighted">',st+26,ed)
            if st == -1:
                break
            else:
                if cf != -1:
                    body=remove_str(body,cf,cf+25)
                    ed=body.find('</span>',order)
                    body=remove_str(body,ed,ed+6)
                else:
                    where[st+26] = str(ed-1)
                    order=ed+7

        for key,value in where.items():
            key = str(key)
            value = str(value)
            if secret == '':
                secret = key + ':' + value
            else:
                secret += ','+ key + ':'+ value

        con = get_db()

        sql = "UPDATE archives SET body = ?, secret = ?, date = ? WHERE id = ?"
        con.execute(sql, (body, secret, date, id))
        con.commit()
        con.close()
        time.sleep(2)
        return redirect(url_for('complete'))
    else:
        return redirect(url_for("top",status="logout"))

@app.route("/login",methods=["GET" , "POST"])
def login():
    if request.method == 'POST':
        user_name = request.form["user_name"]
        user = User.query.filter_by(user_name=user_name).first()
        if user:
            password = request.form["password"]
            SALT = user.salt
            hashed_password = sha256((user_name + password + SALT).encode("utf-8")).hexdigest()
            if user.hashed_password == hashed_password:
                session["user_name"] = user_name
                return redirect(url_for("index"))
            else:
                return redirect(url_for("login",status="wrong_password"))
        else:
            return redirect(url_for("login",status="user_notfound"))
    else:
        status = request.args.get("status")
        return render_template("login.html",status=status)

@app.route("/logout")
def logout():
    session.pop("user_name", None)
    return redirect(url_for("top",status="logout"))

@app.route('/new',methods= ["GET"])
def new():
    return render_template('new.html')

@app.route("/registar",methods=["POST"])
def registar():
    user_name = request.form["user_name"]
    user = User.query.filter_by(user_name=user_name).first()
    if user:
        return redirect(url_for("/new",status="exist_user"))
    else:
        password = request.form["password"]
        salt = randomname(32)
        hashed_password = sha256((user_name + password + salt).encode("utf-8")).hexdigest()
        user = User(user_name, hashed_password,salt)
        db_session.add(user)
        db_session.commit()
        session["user_name"] = user_name
        return redirect(url_for("index"))



if __name__ == "__main__":
    app.run(debug=True)
