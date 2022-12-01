from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
import json
import copy
from object_definition import options, breakdowns, stepfun
from helper_funcs import dict_hash, freq_text_to_int
import analysis

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

    __tablename__ = "records2"

    id = db.Column(db.Integer, primary_key=True)
    #add date
    uid = db.Column(db.String(4096))
    breakdown = db.Column(db.PickleType())
    adult1 = db.Column(db.Integer())
    adult2 = db.Column(db.Integer())
    child = db.Column(db.Integer())
 

@app.route("/allresults", methods=["GET"])
def all_results():
    return render_template("all_results.html", records=Record.query.all())

@app.route("/results/<uid>", methods=["GET"])
def display_results(uid):

    n_adults = request.args.get('nadult', default='1')
    n_children = request.args.get('nchild', default='0')

    record=db.session.execute(db.select(Record).filter_by(uid=uid)).first()
    
    for rec in record: #only one of these
        national_results, household_vars = analysis.run(rec.adult1, rec.adult2, rec.child, int(n_adults), int(n_children))

    return render_template("result_page.html", results=national_results, vars=json.dumps(household_vars))

@app.route("/page3", methods=["GET", "POST"])
def custom_control():

    n_adults = request.args.get('nadult', default='1')
    n_children = request.args.get('nchild', default='0')
    mainoption = request.args.get('mainoption', default='1')

    breakdown = copy.deepcopy(breakdowns[int(mainoption)-1])
    maxop = breakdowns[-1]
    
    if request.method == "GET":

        for cat, maxcat in zip(breakdown, maxop):
            cat['value'] = cat['adult1'] * (1 + (int(n_adults)-1)*cat['adult2rat'] + int(n_children)*cat['childrat'])
            cat['max'] = maxcat['adult1'] * (1 +(int(n_adults)-1)*maxcat['adult2rat'] + int(n_children)*maxcat['childrat'])
            cat['step'] = stepfun(cat['max'])

        return render_template("custom_control.html", breakdown=breakdown, 
            n_adults=n_adults, n_children=n_children, mainoption=mainoption)

    
    totals={'adult1': 0, 'adult2': 0, 'child': 0}

    for cat in breakdown:
        effratio = 1 + (int(n_adults)-1)*cat['adult2rat'] + int(n_children)*cat['childrat']        
        val = int(request.form[cat['name']])/effratio

        cat['adult1'] = val
        del cat['description'] 

        totals['adult1'] +=  freq_text_to_int(cat['freq']) * val
        totals['adult2'] += freq_text_to_int(cat['freq']) * cat['adult2rat'] * val
        totals['child'] += freq_text_to_int(cat['freq']) * cat['childrat'] * val

    uid = dict_hash(breakdown)
    record = Record(uid=uid, breakdown=breakdown, adult1=totals['adult1'], adult2=totals['adult2'], child=totals['child'])
    db.session.add(record)
    db.session.commit()
    return redirect(url_for('display_results', uid=uid) + '?nadult=' + n_adults + '&nchild='+ n_children)

@app.route("/page2", methods=["GET", "POST"])
def main_control():

    n_adults = request.args.get('nadult', default='1')
    n_children = request.args.get('nchild', default='0')

    if request.method == "GET":        

        for opt in options:
            opt['value']=opt['adult1'] *(1 + (int(n_adults)-1)*opt['adult2rat'] + int(n_children)*opt['childrat'])

        return render_template("main_control.html", options=json.dumps(options),
         n_adults=n_adults, n_children=n_children)

    mainoption=request.form["mainoption"]

    return redirect(url_for('custom_control') + '?nadult=' + n_adults + '&nchild='+ n_children + '&mainoption=' + mainoption)

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