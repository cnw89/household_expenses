from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
import json
import datetime
from object_definition import options, prep_expenses_for_serving, \
      prep_expenses_for_recording, prep_lifetime_for_recording, reprep_breakdown
from helper_funcs import dict_hash
import analysis
from analysis import dequivalize

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
    """
    If updating record structure:
    in python terminal:
    from app import db
    db.create_all()
    """
    __tablename__ = "records"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime())
    uid = db.Column(db.String(4096))
    total_equivalized_spend = db.Column(db.Integer())
    breakdown = db.Column(db.String(4096))
    lifetime_breakdown = db.Column(db.String(4096))
    savings_pc = db.Column(db.Integer())
    pension_pc = db.Column(db.Integer())
    retirement_pc = db.Column(db.Integer())
    n_adults = db.Column(db.Integer())
    n_children = db.Column(db.Integer())
 

@app.route("/allresults", methods=["GET"])
def all_results():
    return render_template("all_results.html", records=Record.query.all())

@app.route("/questions", methods=["GET"])
def questions():
    return render_template("further_questions.html")

@app.route("/results/<uid>", methods=["GET"])
def display_results(uid):

    record=db.session.execute(db.select(Record).filter_by(uid=uid)).first()
    
    for rec in record: #only one of these
        
        n_adults = int(request.args.get('nadult', default=rec.n_adults))
        n_children = int(request.args.get('nchild', default=rec.n_children))
        
        d_common, d_howmuch, d_whohas, d_dowe, d_willgrowth = analysis.run(rec.total_equivalized_spend,
                                                                           json.loads(rec.breakdown),
                                                                           json.loads(rec.lifetime_breakdown),
                                                                           rec.savings_pc,
                                                                           rec.pension_pc,
                                                                           rec.retirement_pc,
                                                                           n_adults,
                                                                           n_children)
        

    return render_template("result_page.html", 
                            d_common=d_common,
                            d_howmuch=d_howmuch, 
                            d_whohas=d_whohas,
                            d_dowe=d_dowe, 
                            d_willgrowth=d_willgrowth)

@app.route("/page5/<uid>", methods=["GET", "POST"])
def retirement_control(uid):

    if request.method == "GET":
        
        retirement_data = {}
        retirement_data['value'] = 100

        return render_template("retirement_control.html", retirement=retirement_data, uid=uid)

    records=db.session.execute(db.select(Record).filter_by(uid=uid)).first()
    rec = records[0]
    
    rec.retirement_pc = int(request.form['Retirement'])
    db.session.commit()

    return redirect(url_for('display_results', uid=uid))

@app.route("/page4/<uid>", methods=["GET", "POST"])
def lifetime_control(uid):

    if request.method == "GET":
        
        return render_template("lifetime_control.html", uid=uid)

    records=db.session.execute(db.select(Record).filter_by(uid=uid)).first()
    rec = records[0]
    
    lifetime_breakdown, breakdown = prep_lifetime_for_recording(request.form, 
                                                                json.loads(rec.breakdown),
                                                                rec.n_adults,
                                                                rec.n_children)

    rec.breakdown = json.dumps(breakdown)
    rec.lifetime_breakdown = json.dumps(lifetime_breakdown)
    db.session.commit()

    return redirect(url_for('retirement_control', uid=uid))

@app.route("/page3", methods=["GET", "POST"])
def custom_control():

    uid = request.args.get('uid', default='0') #only provided if going back from next page

    if uid != '0':            
        records=db.session.execute(db.select(Record).filter_by(uid=uid)).first()
        rec = records[0]
        breakdown = json.loads(rec.breakdown)
        breakdown = reprep_breakdown(breakdown, rec.savings_pc, rec.pension_pc)
        n_adults = rec.n_adults
        n_children = rec.n_children
        n_adults_s = str(n_adults)
        n_children_s = str(n_children)

    else:
        n_adults_s = request.args.get('nadult', default='1')
        n_children_s = request.args.get('nchild', default='0')
        breakdown = request.args.get('mainoption', default='0')
        n_adults = int(n_adults_s)
        n_children = int(n_children_s)
        
    if request.method == "GET":        
        
        breakdown_data_list, savings_data, pension_data = prep_expenses_for_serving(breakdown, n_adults, n_children)
        
        return render_template("custom_control.html", 
                breakdown=breakdown_data_list, 
                savings=savings_data, 
                pension=pension_data,
                n_adults=n_adults_s, 
                n_children=n_children_s)

    
    total_equivalized_spend, breakdown, savings_pc, pension_pc = prep_expenses_for_recording(request.form, 
                                                                                                     n_adults,
                                                                                                     n_children)
    
    #make up some dummy values for things we haven't set yet
    lifetime_breakdown = {}
    retirement_pc = -1

    uid = dict_hash(breakdown) #even if we were passed a uid we need to create a new one as the inputs have changed
    now = datetime.datetime.now()
    record = Record(date=now, 
                    uid=uid, 
                    total_equivalized_spend=total_equivalized_spend, 
                    breakdown=json.dumps(breakdown),
                    lifetime_breakdown=json.dumps(lifetime_breakdown),
                    savings_pc=savings_pc, 
                    pension_pc=pension_pc, 
                    retirement_pc=retirement_pc,
                    n_adults=n_adults, 
                    n_children=n_children)

    db.session.add(record)
    db.session.commit()

    return redirect(url_for('lifetime_control', uid=uid))

@app.route("/page2", methods=["GET", "POST"])
def main_control():

    n_adults_s = request.args.get('nadult', default='1')
    n_children_s = request.args.get('nchild', default='0')
    n_adults = int(n_adults_s)
    n_children = int(n_children_s)

    if request.method == "GET":        

        for opt in options:
            opt['value']=dequivalize(opt['equivalized_spend'], n_adults, n_children)

        return render_template("main_control.html", options=json.dumps(options),
         n_adults=n_adults_s, n_children=n_children_s)

    mainoption=request.form["mainoption"]

    return redirect(url_for('custom_control') + '?nadult=' + n_adults_s + '&nchild='+ n_children_s + '&mainoption=' + mainoption)

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