from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
import secrets
import string
import json
from object_definition import options

localdb = True
app = Flask(__name__)

app.config["DEBUG"] = True

if localdb: #running locally
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username="localuser",
        password="4GmDuEH#8Rsx",
        hostname="localhost:3306",
        databasename="test1",
    )
else: #running on pythonAnywhere
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username="cnwarwick",
        password="4GmDuEH#8Rsx",
        hostname="cnwarwick.mysql.pythonanywhere-services.com",
        databasename="cnwarwick$expense1",
    )


app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Record(db.Model):

    __tablename__ = "records"

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(4096))
    content = db.Column(db.String(4096))
 

@app.route("/allresults", methods=["GET"])
def all_results():
    return render_template("all_results.html", records=Record.query.all())

@app.route("/results/<uid>", methods=["GET"])
def display_results(uid):
    record=db.session.execute(db.select(Record).filter_by(uid=uid)).one()
    return render_template("result_page.html", records=record)

@app.route("/page3", methods=["GET", "POST"])
def custom_control():
    if request.method == "GET":

        mainoption = request.args.get('mainoption', default='1')
        return render_template("custom_control.html", startValues=mainoption)

    uid = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(7))
    record = Record(uid=uid, content=request.form["contents"])
    db.session.add(record)
    db.session.commit()
    return redirect(url_for('display_results', uid=uid))

@app.route("/page2", methods=["GET", "POST"])
def main_control():
    if request.method == "GET":

        n_adults = int(request.args.get('nadult', default='2'))
        n_children = int(request.args.get('nchild', default='0'))

        for opt in options:
            opt['value']=opt['adult1'] + (n_adults-1)*opt['adult2'] + n_children*opt['child']

        return render_template("main_control.html", options=json.dumps(options))

    mainoption=request.form["mainoption"]

    return redirect(url_for('custom_control') + '?mainoption=' + mainoption)

@app.route("/page1", methods=["GET", "POST"])
def user_info():
    if request.method == "GET":
        return render_template("user_info.html")

    n_children=request.form["n_children"]
    n_adults=request.form["n_adults"]
    #do something with request.form
    return redirect(url_for('main_control') + '?nadult=' + n_adults + '&nchild='+ n_children )

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("landing.html")

    return redirect(url_for('user_info'))

if __name__ == '__main__':
    app.run(debug=True)