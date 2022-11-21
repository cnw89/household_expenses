from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
import secrets
import string

localdb = True
app = Flask(__name__)

#columns=['Item', 'Payments/year', 'First Adult', 'Subsequent Adults', 'Children'])
EXPENSES = {'Food': [52, 50, 40, 30], 
    'Housing': [12, 400, 300, 200], 
    'Clothing': [12, 50, 50, 35]}

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

# def abort_if_value_is_not_valid(item_id, value):

#     print(value)
#     #some of these are probably redundant because of argparser handling
#     if type(value) is not list:
#         print(type(value))        
#         abort(404, message="Item {} has invalid value {} - not list".format(item_id, value))

#     if len(value) != 4:
#         print(len(value))
#         abort(404, message="Item {} has invalid value {} - not length 4".format(item_id, value))

#     if not all(isinstance(v, int) for v in value):
#         abort(404, message="Item {} has invalid value {} - not ints".format(item_id, value))

# parser = reqparse.RequestParser()
# for item in EXPENSES:
#     parser.add_argument(item, type=int, action='append')


# # ExpenseQuery
# # shows a list of all EXPENSES, and lets you POST new values of expenses
# class ExpenseQuery(Resource):
#     def get(self):
#         return EXPENSES

#     def post(self):
#         args = parser.parse_args()
        
#         for item in args:
            
#             abort_if_value_is_not_valid(item, args[item])

#             EXPENSES[item] = args[item]

#         #instead of returning expenses, return data regarding affordability for
#         #households
#         return EXPENSES, 201

# # ExpenseRecord
# # gets the data related to a single record ID 
# class ExpenseRecord(Resource):
#     def get(self, id):

#         #check if valid id
    
#         #return expenses of valid id from sql database
#         return db.session.get(Record, id)

# #get all valid record IDs, or post a new one
# class ExpenseRecordList(Resource):
    
#     def get(self):
        
#         return Record.query.all()

#     def post(self):
#         args = parser.parse_args()
        
#         for item in args:
            
#             abort_if_value_is_not_valid(item, args[item])

#             EXPENSES[item] = args[item]
        
#         #then write expenses to sql database

#         #generate long random id
#         uid = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(7))
#         record = Record(content=uid)
#         db.session.add(record)
#         db.session.commit()
        
#         #return id of expense record
#         return uid, 201        
@app.route("/results/<uid>", methods=["GET"])
def display_results(uid):
    record=db.session.execute(db.select(Record).filter_by(uid=uid)).one()
    return render_template("result_page.html", records=record)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_page.html", records=Record.query.all())

    uid = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(7))
    record = Record(uid=uid, content=request.form["contents"])
    db.session.add(record)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)