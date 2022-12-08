import math 
op1 = {'name' : 'Survive', 'equivalized_spend': 100, 'description': 'asdasdasd'}
op2 = {'name' : 'Modern essentials', 'equivalized_spend': 100, 'description': 'asdasdasd'}
op3 = {'name' : 'Basic comforts', 'equivalized_spend': 100, 'description': 'asdasdasd'}
op4 = {'name' : 'Little luxuries', 'equivalized_spend': 100, 'description': 'asdasdasd'}
op5 = {'name' : 'Larger luxuries', 'equivalized_spend': 100, 'description': 'asdasdasd'}
options = [op1, op2, op3, op4, op5]
#options = ['Survive','Modern essentials','Basic comforts','Little luxuries','Larger luxuries']

#Categories for op1
cat1 = {'name' : 'Food', 'freq': 'week', 'equivalized_spend': 100, 'description': 'asdasdasd'}
cat2 = {'name' : 'Housing', 'freq': 'month', 'equivalized_spend': 100, 'description': 'asdasdasd'}
cat3 = {'name' : 'Clothing', 'freq': 'year', 'equivalized_spend': 100, 'description': 'asdasdasd'}
op1 = [cat1, cat2, cat3]

#values for max
cat1 = {'name' : 'Food', 'freq': 'week', 'equivalized_spend': 1000, 'description': 'asdasdasd'}
cat2 = {'name' : 'Housing', 'freq': 'month', 'equivalized_spend': 1000, 'description': 'asdasdasd'}
cat3 = {'name' : 'Clothing', 'freq': 'year', 'equivalized_spend': 1000, 'description': 'asdasdasd'}
maxop = [cat1, cat2, cat3]

#all options
breakdowns = [op1, op1, op1, op1, op1, maxop]
cats = ['Food', 'Housing', 'Clothing']
#stepfun
stepfun = lambda m : 10 * math.ceil(m/1000)

#columns=['Item', 'Payments/year', 'First Adult', 'Subsequent Adults', 'childratren'])
EXPENSES = {'Food': [52, 0.75, 40, 30], 
    'Housing': [12, 400, 300, 200], 
    'Clothing': [12, 0.75, 0.75, 35]}