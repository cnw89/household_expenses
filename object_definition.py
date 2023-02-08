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
from pathlib import Path
THIS_FOLDER = Path(__file__).parent.resolve()

filename = THIS_FOLDER / "expense_presets.xlsx"

wb = load_workbook(filename)

options, optlist = generate_mainoptions(wb['mainoptions'])

breakdowns, catlist = generate_breakdowns(wb, optlist)

# #stepfun
stepfun = lambda m : 10 * math.ceil(m/1000)