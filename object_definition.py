from openpyxl import load_workbook
from pathlib import Path
import copy
from analysis import equivalize, dequivalize, NON_RETIRED_HOUSEHOLD_YEARS, AVERAGE_CHILDREN_PER_HOUSE

THIS_FOLDER = Path(__file__).parent.resolve()

filename = THIS_FOLDER / "expense_presets.xlsx"

optkeys = ['name', 'equivalized_spend', 'description']
catkeys = ['name', 'id', 'description']

retirement_values = [100, 90, 80, 70, 60]

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
    
    #TODO: overide max value for housing to be independent of equivalization

    if type(mainoption) is dict: #passed a breakdown instead of a mainoption value
        breakdown = mainoption
    else:
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
        if (cat['name'] == 'Housing'):
            cat_data['max'] = max(dequivalize(maxop[catname], max(n_adults+1, 4), n_children), 2 * cat_data['value'])
        else:
            cat_data['max'] = max(dequivalize(maxop[catname], n_adults+1, n_children), 2 * cat_data['value'])
        cat_data['step'] = 10#stepfun(cat_data['max'])

        breakdown_data_list.append(cat_data)

    return breakdown_data_list, savings_data, pension_data

def reprep_breakdown(breakdown, savings_pc, pension_pc):

    breakdown_out = {}
    for cat in catlist:
        if (cat == 'Savings'):
            continue
        elif (cat == 'Pension'):
            continue

        #now switch to annual:
        breakdown_out[cat] = breakdown[cat]/12        

    breakdown_out['Savings'] = savings_pc

    breakdown_out['Pension'] = pension_pc

    return breakdown_out

def prep_expenses_for_recording(form, n_adults, n_children):

    if form['displayFrequency'] == 'yearly':
        freq_factor = 1
    elif form['displayFrequency'] == 'weekly':
        freq_factor = 52
    else: 
        freq_factor = 12
    
    total_equivalized_spend=0
    breakdown = {}
    for cat in catlist:
        if (cat == 'Savings'):
            continue
        elif (cat == 'Pension'):
            continue

        #now switch to annual:
        breakdown[cat] = freq_factor * equivalize(int(form[cat]), n_adults, n_children)        

        total_equivalized_spend +=  breakdown[cat]               

    #saving pc is a pc of income not expense
    savings_pc = int(form['Savings'])
    breakdown['Savings'] = total_equivalized_spend * (savings_pc/(100-savings_pc))
    total_equivalized_spend += breakdown['Savings']

    #pension pc is a pc of income not expense, including savings
    pension_pc = int(form['Pension'])
    breakdown['Pension'] = total_equivalized_spend * (pension_pc/(100-pension_pc))
    total_equivalized_spend += breakdown['Pension']

    return total_equivalized_spend, breakdown, savings_pc, pension_pc

def prep_lifetime_for_recording(form, breakdown, n_adults, n_children):

    lifetime_breakdown = {} #for storing non-averaged lifetime payments

    #averaged house downpayment
    house = int(form['house'])
    lifetime_breakdown['House_deposit'] = house
    breakdown['House_deposit'] = equivalize(house/NON_RETIRED_HOUSEHOLD_YEARS, n_adults, n_children)  

    #Averaged Pre-school childcare fees 
    childcare = int(form['childcare']) * 12 #months
    childcare_years = float(form['childcare_years'])
    lifetime_breakdown['Childcare'] = childcare
    lifetime_breakdown['Childcare_years'] = childcare_years
    breakdown['Childcare'] = equivalize(childcare * childcare_years * 
                                        AVERAGE_CHILDREN_PER_HOUSE/NON_RETIRED_HOUSEHOLD_YEARS, 
                                        n_adults, n_children)
    
    return lifetime_breakdown, breakdown