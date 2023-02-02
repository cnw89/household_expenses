from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
import json
import copy
from object_definition import options, breakdowns, stepfun, optlist, catlist
from helper_funcs import dict_hash, freq_text_to_int
import analysis
from analysis import equivalize, dequivalize

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
    __tablename__ = "records4"

    id = db.Column(db.Integer, primary_key=True)
    #add date
    uid = db.Column(db.String(4096))
    breakdown = db.Column(db.PickleType())
    total_equivalized_spend = db.Column(db.Integer())
    pension_pc = db.Column(db.Integer())
    n_adults = db.Column(db.Integer())
    n_children = db.Column(db.Integer())
 

@app.route("/allresults", methods=["GET"])
def all_results():
    return render_template("all_results.html", records=Record.query.all())

@app.route("/results/<uid>", methods=["GET"])
def display_results(uid):

    record=db.session.execute(db.select(Record).filter_by(uid=uid)).first()
    
    for rec in record: #only one of these
        
        d_common, d_howmuch, d_whohas, d_dowe, d_willgrowth = analysis.run(rec.total_equivalized_spend, rec.pension_pc)

        n_adults = int(request.args.get('nadult', default=rec.n_adults))
        n_children = int(request.args.get('nchild', default=rec.n_children))

        d_common['n_adults'] = n_adults
        d_common['n_children'] = n_children

    return render_template("result_page2.html", 
                            d_common=d_common,
                            d_howmuch=d_howmuch, 
                            d_whohas=d_whohas,
                            d_dowe=d_dowe, 
                            d_willgrowth=d_willgrowth)

@app.route("/page3", methods=["GET", "POST"])
def custom_control():

    n_adults_s = request.args.get('nadult', default='1')
    n_children_s = request.args.get('nchild', default='0')
    mainoption = request.args.get('mainoption', default='0')

    n_adults = int(n_adults_s)
    n_children = int(n_children_s)

    breakdown = copy.deepcopy(breakdowns[optlist[int(mainoption)]])
    maxop = breakdowns['max']
    breakdown_data_list = []

    if request.method == "GET":
        
        for cat in catlist:
            
            if (cat['name'] == 'Savings'):
                savings_data = cat
                savings_data['id'] = 'Savings'
                savings_data['value'] = breakdown['Savings']
                savings_data['max'] = maxop['Savings']
                savings_data['step'] = 1
                continue
            elif (cat['name'] == 'Pension'):
                pension_data = cat
                pension_data['id'] = 'Pension'
                pension_data['value'] = breakdown['Pension']
                pension_data['max'] = maxop['Pension']
                pension_data['step'] = 1
                continue

            cat_data = {}
            catname = cat['name']
            cat_data['name'] = catname
            cat_data['id'] = cat['id']
            cat_data['description'] = cat['description']
            cat_data['value'] = dequivalize(breakdown[catname], n_adults, n_children)
            cat_data['freq'] = 'month'
            cat_data['max'] = max(dequivalize(maxop[catname], n_adults+2, n_children), 2 * cat_data['value'])
            cat_data['step'] = 1#stepfun(cat_data['max'])

            breakdown_data_list.append(cat_data)

        return render_template("custom_control.html", 
                breakdown=breakdown_data_list, 
                savings=savings_data, 
                pension=pension_data,
                n_adults=n_adults_s, 
                n_children=n_children_s, 
                mainoption=mainoption)

    
    total_equivalized_spend=0

    for cat in breakdown:
        if (cat == 'Savings'):
            continue
        elif (cat == 'Pension'):
            continue

        breakdown[cat] = equivalize(int(request.form[cat]), n_adults, n_children)        

        total_equivalized_spend +=  12 * breakdown[cat]               
    
    #saving pc is a pc of income not expense
    savings_pc = int(request.form['Savings'])
    breakdown['Savings'] = total_equivalized_spend * (savings_pc/(100-savings_pc))
    total_equivalized_spend += breakdown['Savings']

    #pension pc is a pc of income not expense, including savings
    pension_pc = int(request.form['Pension'])
    breakdown['Pension'] = total_equivalized_spend * (pension_pc/(100-pension_pc))
    total_equivalized_spend += breakdown['Pension']

    uid = dict_hash(breakdown)
    record = Record(uid=uid, breakdown=breakdown, total_equivalized_spend=total_equivalized_spend, 
        pension_pc=pension_pc, n_adults=n_adults, n_children=n_children)

    db.session.add(record)
    db.session.commit()

    return redirect(url_for('display_results', uid=uid))

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