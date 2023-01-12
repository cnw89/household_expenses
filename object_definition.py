import math 
from openpyxl import load_workbook
optkeys = ['name', 'equivalized_spend', 'description']
catkeys = ['name', 'id', 'description']

def generate_mainoptions(ws):

    opts = []
    for row in ws.values:
        opt = { k: v for k, v in zip(optkeys, row)}

        opts.append(opt)

    optlist = [opt['name'] for opt in opts]

    return opts, optlist

def generate_breakdowns(wb, optlist):

    ws = wb['categories']
    cats = []
    for row in ws.values:
        cat = { k: v for k, v in zip(catkeys, row)}

        cats.append(cat)
    
    catlist = [cat['name'] for cat in cats]

    ws = wb['breakdowns']
    breakdowns = {}
    optlist.append('max')

    for iopt, row in enumerate(ws.values):

        breakdowns[optlist[iopt]] = {cat : val for cat, val in zip(catlist, row)}

    return breakdowns, cats

#if __name__ == "__main__":

filename = 'expense_presets.xlsx'

wb = load_workbook(filename)

options, optlist = generate_mainoptions(wb['mainoptions'])
#print(options)
breakdowns, catlist = generate_breakdowns(wb, optlist)
#print(breakdowns)

# op1 = {'name' : 'Survive', 'equivalized_spend': 100, 'description': 'asdasdasd'}
# op2 = {'name' : 'Modern essentials', 'equivalized_spend': 100, 'description': 'asdasdasd'}
# op3 = {'name' : 'Basic comforts', 'equivalized_spend': 100, 'description': 'asdasdasd'}
# op4 = {'name' : 'Little luxuries', 'equivalized_spend': 100, 'description': 'asdasdasd'}
# op5 = {'name' : 'Larger luxuries', 'equivalized_spend': 100, 'description': 'asdasdasd'}
# options = [op1, op2, op3, op4, op5]
# #options = ['Survive','Modern essentials','Basic comforts','Little luxuries','Larger luxuries']

# #Categories for op1
# cat1 = {'name' : 'Food', 'freq': 'week', 'equivalized_spend': 100, 'description': 'asdasdasd'}
# cat2 = {'name' : 'Housing', 'freq': 'month', 'equivalized_spend': 100, 'description': 'asdasdasd'}
# cat3 = {'name' : 'Clothing', 'freq': 'year', 'equivalized_spend': 100, 'description': 'asdasdasd'}
# op1 = [cat1, cat2, cat3]

# #values for max
# cat1 = {'name' : 'Food', 'freq': 'week', 'equivalized_spend': 1000, 'description': 'asdasdasd'}
# cat2 = {'name' : 'Housing', 'freq': 'month', 'equivalized_spend': 1000, 'description': 'asdasdasd'}
# cat3 = {'name' : 'Clothing', 'freq': 'year', 'equivalized_spend': 1000, 'description': 'asdasdasd'}
# maxop = [cat1, cat2, cat3]

# #all options
# breakdowns = [op1, op1, op1, op1, op1, maxop]
# cats = ['Food', 'Housing', 'Clothing']
# #stepfun
stepfun = lambda m : 10 * math.ceil(m/1000)