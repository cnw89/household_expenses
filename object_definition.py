import math
from openpyxl import load_workbook
from pathlib import Path
import copy
from analysis import equivalize, dequivalize

THIS_FOLDER = Path(__file__).parent.resolve()

filename = THIS_FOLDER / "expense_presets.xlsx"

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

    return breakdowns, cats, catlist

def generate_lifetimes(wb, optlist):

    ws = wb['lifetime_categories']
    cats = []
    for row in ws.values:
        cat = { k: v for k, v in zip(catkeys, row)}

        cats.append(cat)

    catlist = [cat['name'] for cat in cats]

    ws = wb['lifetime_breakdowns']
    breakdowns = {}
    optlist.append('max')

    for iopt, row in enumerate(ws.values):

        breakdowns[optlist[iopt]] = {cat : val for cat, val in zip(catlist, row)}

    return breakdowns, catlist

wb = load_workbook(filename)

options, optlist = generate_mainoptions(wb['mainoptions'])

breakdowns, cats, catlist = generate_breakdowns(wb, optlist)

lifetime_breakdowns, lifetime_catlist = generate_lifetimes(wb, optlist)

def prep_expenses_for_serving(mainoption, n_adults, n_children):
    

    breakdown = copy.deepcopy(breakdowns[optlist[int(mainoption)]])
    maxop = breakdowns['max']
    breakdown_data_list = []

    for cat in cats:
            
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

    return breakdown_data_list, savings_data, pension_data
