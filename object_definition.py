import math 
op1 = {'name' : 'Survive', 'adult1': 100, 'adult2rat':0.75, 'childrat':0.75, 'description': 'asdasdasd'}
op2 = {'name' : 'Modern essentials', 'adult1': 100, 'adult2rat':0.75, 'childrat':0.75, 'description': 'asdasdasd'}
op3 = {'name' : 'Basic comforts', 'adult1': 100, 'adult2rat':0.75, 'childrat':0.75, 'description': 'asdasdasd'}
op4 = {'name' : 'Little luxuries', 'adult1': 100, 'adult2rat':0.75, 'childrat':0.75, 'description': 'asdasdasd'}
op5 = {'name' : 'Larger luxuries', 'adult1': 100, 'adult2rat':0.75, 'childrat':0.75, 'description': 'asdasdasd'}
options = [op1, op2, op3, op4, op5]
#options = ['Survive','Modern essentials','Basic comforts','Little luxuries','Larger luxuries']

#Categories for op1
cat1 = {'name' : 'Food', 'freq': 'week', 'adult1': 100, 'adult2rat':0.75, 'childrat':0.75, 'description': 'asdasdasd'}
cat2 = {'name' : 'Housing', 'freq': 'month', 'adult1': 200, 'adult2rat':0.75, 'childrat':0.75, 'description': 'asdasdasd'}
cat3 = {'name' : 'Clothing', 'freq': 'year', 'adult1': 300, 'adult2rat':0.75, 'childrat':0.75, 'description': 'asdasdasd'}
op1 = [cat1, cat2, cat3]

#values for max
cat1 = {'name' : 'Food', 'freq': 'week', 'adult1': 1000, 'adult2rat':0.75, 'childrat':0.75, 'description': 'asdasdasd'}
cat2 = {'name' : 'Housing', 'freq': 'month', 'adult1': 2000, 'adult2rat':0.75, 'childrat':0.75, 'description': 'asdasdasd'}
cat3 = {'name' : 'Clothing', 'freq': 'year', 'adult1': 3000, 'adult2rat':0.75, 'childrat':0.75, 'description': 'asdasdasd'}
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