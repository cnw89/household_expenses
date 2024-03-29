import types
import pickle
import numpy as np
from scipy.interpolate import interp1d
import check_inputs_safe
import copy 

from pathlib import Path
THIS_FOLDER = Path(__file__).parent.resolve()

#non-retired data
filename = THIS_FOLDER / "income_assessment.pickle"
with open(filename, 'rb') as fID:
    d_nr = pickle.load(fID)

#retired data
filename = THIS_FOLDER / "income_assessment_retired.pickle"
with open(filename, 'rb') as fID:
    d_r = pickle.load(fID)

#dict_keys(['f_HEDI_to_pcInd', 'f_pcInd_to_HEDI', 'tot_households', 'f_pcInd_to_pcHouse',
# 'f_pcInd_to_pcHouse_byComp', 'd_household_comps_to_index', 'f_pcInd_to_required_incomesum',
# 'f_pcInd_to_deficit_below', 'f_pcInd_to_excess_above'])

MIN_WAGE = 10.42 #checked April 2023
DEFAULT_HOURS_PER_WEEK = 37.5

#equivalization factors from OECD-modified standard:
ADULT1 = 1
ADULT2 = 0.5
CHILD = 0.3

UK_GDHI = 1438237*1e6
UK_ANNUAL_GROWTH = 0.015
UK_EMPLOYED = 32813000
AVERAGE_WAGE_BOOST_FACTOR = 1.5
SOCIAL_HOUSING_PER_MONTH = 94.31 * 52/12#https://www.gov.uk/government/news/social-housing-sector-stock-and-rents-statistics-for-202122-show-small-net-increase-in-social-homes#:~:text=The%20average%20increase%20in%20general,different%20regions%20of%20the%20country.
TRANSPORT_CAP_PER_MONTH = 50 * 2 #for two people

#checked April 2023
INCOME_TAX_THRESHOLDS = [125140, 50270, 12570] #annual salary thresholds
INCOME_TAX_RATES = [0.45, 0.4, 0.2]

thresh1 = (INCOME_TAX_THRESHOLDS[1] - INCOME_TAX_THRESHOLDS[2])*(1 - INCOME_TAX_RATES[2]) + INCOME_TAX_THRESHOLDS[2]
thresh2 = (INCOME_TAX_THRESHOLDS[0] - INCOME_TAX_THRESHOLDS[1])*(1 - INCOME_TAX_RATES[1]) + thresh1
INCOME_TAX_THRESHOLDS_INV = [thresh2, thresh1, INCOME_TAX_THRESHOLDS[2]]

#Class 1A national insurance, employee contributions, checked April 2023
NI_THRESHOLDS = [52*967, 52*242.01] #weekly earnings thresholds
NI_RATES = [0.02, 0.12]

COUNCIL_TAX = 1600
STATE_PENSION_PER_WEEK = 203.85 #checked April 2023

thresh1 = (NI_THRESHOLDS[0] - NI_THRESHOLDS[1])*(1 - NI_RATES[1]) + NI_THRESHOLDS[1]
NI_THRESHOLDS_INV = [thresh1, NI_THRESHOLDS[1]]

AVERAGE_CHILDREN_PER_HOUSE = 0.8
NON_RETIRED_HOUSEHOLD_YEARS = 40
SAVE_FOR_FIRST_HOUSE_YEARS = 7

def run(HEDI, breakdown, lifetime_breakdown, savings_pc, pension_pc, retirement_pc, n_adults, n_children):
    """
    HEDI - household equivalized disposable income - equivalized to 2 adults, 0 children.
        - NOT including averaged lifetime expenses
    """

    HEDI_retired = (retirement_pc/100) * (HEDI - breakdown['Pension'] - breakdown['Savings'])
    # values including averaged lifetime values
    HEDI_inc_life = HEDI + breakdown['House_deposit'] + breakdown['Childcare']
    HEDI_retired_inc_life = (retirement_pc/100) * (HEDI_inc_life - breakdown['Pension'] - breakdown['Savings'])

    pc_ind, pc_ind_ret, HEDI_inc_life, HEDI_retired_inc_life, warn_user, warn_text = \
    check_inputs_safe.run(HEDI_inc_life, 
                            HEDI_retired_inc_life, 
                            d_r,
                            d_nr)
    
    #vars directly injected into html with Jinja

    # common variables for use in the text
    d_common = types.SimpleNamespace()
    
    d_common.warn_user = warn_user
    d_common.warn_text = warn_text

    #constants used
    d_common.min_wage = MIN_WAGE
    d_common.default_hours_per_week = DEFAULT_HOURS_PER_WEEK
    d_common.council_tax = COUNCIL_TAX
    d_common.average_children_per_house = AVERAGE_CHILDREN_PER_HOUSE 
    d_common.non_retired_household_years = NON_RETIRED_HOUSEHOLD_YEARS 
    d_common.state_pension_per_week = STATE_PENSION_PER_WEEK

    #monthly
    d_common.first_adult = dequivalize(HEDI, 1, 0)/12
    d_common.second_adult = (dequivalize(HEDI, 2, 0) - dequivalize(HEDI, 1, 0))/12
    d_common.child = (dequivalize(HEDI, 1, 1) - dequivalize(HEDI, 1, 0))/12

    d_common.first_adult_retired = dequivalize(HEDI_retired, 1, 0)/12
    d_common.second_adult_retired = (dequivalize(HEDI_retired, 2, 0) - dequivalize(HEDI_retired, 1, 0))/12

    #personalized for the respondant
    d_common.n_adults = n_adults
    d_common.n_children = n_children
    d_common.base = dequivalize(HEDI, n_adults, n_children)
    d_common.with_tax1 = calc_pre_tax_income_pre_pension(d_common.base, pension_pc)
    d_common.with_tax2 = calc_pre_tax_income_pre_pension(d_common.base/2, pension_pc)
    d_common.hours_1 = d_common.with_tax1/(MIN_WAGE * 52)
    d_common.hours_2 = d_common.with_tax2/(MIN_WAGE * 52)    
    d_common.wage_1 = d_common.with_tax1/(DEFAULT_HOURS_PER_WEEK * 52)
    d_common.wage_2 = d_common.with_tax2/(DEFAULT_HOURS_PER_WEEK * 52)

    d_common.base_retired = dequivalize(HEDI_retired, n_adults, 0)
    #cap state pension at the amount required
    d_common.state_pension = n_adults * STATE_PENSION_PER_WEEK*52

    #other variables organised by infographic
    #1 how much is enough
    d_howmuch = types.SimpleNamespace()
    adults = [1, 1, 2, 2, 2, 2]
    children = [0, 1, 0, 1, 2, 3]
    d_howmuch.base = [dequivalize(HEDI, na, nc) for (na, nc) in zip(adults, children)]
    d_howmuch.with_tax1 = [calc_pre_tax_income_pre_pension(sal, pension_pc) for sal in d_howmuch.base]
    d_howmuch.with_tax2 = [calc_pre_tax_income_pre_pension(sal/min(2, na), pension_pc) for sal, na in zip(d_howmuch.base, adults)]

    d_howmuch.save_for_first_house_years = SAVE_FOR_FIRST_HOUSE_YEARS
    d_howmuch.while_saving_for_first_house = (lifetime_breakdown['House_deposit']/SAVE_FOR_FIRST_HOUSE_YEARS) 
    d_howmuch.while_preschool_childcare = lifetime_breakdown['Childcare'] 

    adults = [1, 2]
    children = [0, 0]
    d_howmuch.base_retired = [calc_pre_tax_income_retired(dequivalize(HEDI_retired, na, nc)).item() \
                               for (na, nc) in zip(adults, children)]
    #cap state pension at the amount required
    d_howmuch.state_pension = [min(na * STATE_PENSION_PER_WEEK*52, limit) for (na, limit) in zip(adults, d_howmuch.base_retired)]
    #excess to state pension:
    d_howmuch.private_pension = [base - state for (base, state) in zip(d_howmuch.base_retired, d_howmuch.state_pension)]
    
    #what does it take to earn enough calculated in browser from how much is enough...

    #2 who has enough
    d_whohas = types.SimpleNamespace()
    d_whohas.pc_individuals_without_enough_nonretired = 100 * pc_ind
    d_whohas.pc_individuals_without_enough_retired = 100 * pc_ind_ret
    d_whohas.pc_individuals_without_enough_all = (d_whohas.pc_individuals_without_enough_nonretired * d_nr['tot_individuals']
                                                  + d_whohas.pc_individuals_without_enough_retired * d_r['tot_individuals']) \
                                                  / (d_nr['tot_individuals'] + d_r['tot_individuals'])

    #just for nonretired
    d_whohas.pc_enough_by_decile = [dec/HEDI_inc_life for dec in d_nr['l_deciles_av'] ]

    #3 do we have enough
    d_dowe = types.SimpleNamespace()
    d_dowe.uk_gdhi = UK_GDHI
    d_dowe.enough_for_everyone = d_nr['f_pcInd_to_required_incomesum'](pc_ind).item() \
        + d_r['f_pcInd_to_required_incomesum'](pc_ind_ret).item()
    d_dowe.enough_for_everyone_ratio = d_dowe.enough_for_everyone/UK_GDHI
    d_dowe.deficit_without_enough = d_nr['f_pcInd_to_deficit_below'](pc_ind).item() \
        + d_r['f_pcInd_to_deficit_below'](pc_ind_ret).item()
    d_dowe.deficit_without_enough_ratio = d_dowe.deficit_without_enough/UK_GDHI

    #average amount of earnings per employed person
    d_dowe.UK_employed = UK_EMPLOYED
    d_dowe.enough_for_everyone_per_employed = d_dowe.enough_for_everyone/UK_EMPLOYED
    #now find combo of wage and hours
    hours_to_try = np.arange(37.5, 5, -2.5)
    for hours in hours_to_try:
        earnings_with_min_wage = hours * 52 * MIN_WAGE * AVERAGE_WAGE_BOOST_FACTOR
        if earnings_with_min_wage < d_dowe.enough_for_everyone_per_employed:
            break
    wage = d_dowe.enough_for_everyone_per_employed / (hours * 52)
    d_dowe.example_hours = hours
    d_dowe.example_wage = wage

    #4 will growth
    d_willgrowth = types.SimpleNamespace() 
    d_willgrowth.years = [1977, 2021]
    d_willgrowth.growth_bottom = 1.5
    d_willgrowth.growth_top = 2.2
    d_willgrowth.growth_UK = 1.9
    d_willgrowth.bottom_growth_to_enough = 100 * (1/d_whohas.pc_enough_by_decile[0] - 1)
    d_willgrowth.bottom_years_to_enough = years_of_growth(d_willgrowth.bottom_growth_to_enough/100, d_willgrowth.growth_bottom/100)

    #FLATTENING INCOME
    #find fraction of wealth over a multiple of enough, which is 
    tax_thresh_ratio = min(3, np.floor(2*d_whohas.pc_enough_by_decile[-1])/2) # to the nearest 0.5
    if tax_thresh_ratio >= 1:
        pc_ind_tax_thresh = d_nr['f_HEDI_to_pcInd'](HEDI_inc_life * tax_thresh_ratio)
        excess_over_tax_thresh = d_nr['f_pcInd_to_excess_above'](pc_ind_tax_thresh)

        while (excess_over_tax_thresh < d_dowe.deficit_without_enough) and (tax_thresh_ratio > 1):
            tax_thresh_ratio -= 0.5
            pc_ind_tax_thresh = d_nr['f_HEDI_to_pcInd'](HEDI_inc_life * tax_thresh_ratio)
            excess_over_tax_thresh = d_nr['f_pcInd_to_excess_above'](pc_ind_tax_thresh)

        if (excess_over_tax_thresh >= d_dowe.deficit_without_enough) and (tax_thresh_ratio >= 1):
            tax_rate = d_dowe.deficit_without_enough/excess_over_tax_thresh
            d_willgrowth.tax_rate = 100 * tax_rate
            d_willgrowth.tax_thresh_ratio = tax_thresh_ratio
            d_willgrowth.tax_found = True            

            d_willgrowth.taxed = []
            d_willgrowth.credited = []
            d_willgrowth.pc_enough_post_tax_by_decile = []

            for pc in d_whohas.pc_enough_by_decile:
                if pc > tax_thresh_ratio:
                    new_pc = pc - (pc - tax_thresh_ratio)*tax_rate
                else:
                    new_pc = pc

                d_willgrowth.pc_enough_post_tax_by_decile.append(new_pc)
                d_willgrowth.taxed.append(pc - new_pc)
                d_willgrowth.credited.append(max(0, 1 - pc))

        else:
            d_willgrowth.tax_found = False
    else:
        d_willgrowth.tax_found = False

    #COST OF LIVING SAVINGS
    d_willgrowth.cost_caps_per_month = {}
    d_willgrowth.savings_per_year = {}
    d_willgrowth.savings_per_year_retired = {}

    #housing
    d_willgrowth.cost_caps_per_month['housing'] = SOCIAL_HOUSING_PER_MONTH
    breakdown_copy = copy.deepcopy(breakdown)
    breakdown_copy['Housing'] = d_willgrowth.cost_caps_per_month['housing']
    new_cost, new_cost_retired = update_total_equivalized_spend(breakdown_copy, savings_pc, pension_pc, retirement_pc)
    d_willgrowth.savings_per_year['housing'] = max(0, (HEDI - new_cost))
    d_willgrowth.savings_per_year_retired['housing'] = max(0, (HEDI_retired - new_cost_retired))

    #transport
    d_willgrowth.cost_caps_per_month['transport'] = TRANSPORT_CAP_PER_MONTH
    breakdown_copy = copy.deepcopy(breakdown)
    breakdown_copy['Transport'] = d_willgrowth.cost_caps_per_month['transport']
    new_cost, new_cost_retired = update_total_equivalized_spend(breakdown_copy, savings_pc, pension_pc, retirement_pc)
    d_willgrowth.savings_per_year['transport'] = max(0, (HEDI - new_cost))
    d_willgrowth.savings_per_year_retired['transport'] = max(0, (HEDI_retired - new_cost_retired))

    #combined
    d_willgrowth.total_savings = 0
    for sav in d_willgrowth.savings_per_year.values():
        d_willgrowth.total_savings += sav

    d_willgrowth.total_savings_retired = 0    
    for sav in d_willgrowth.savings_per_year_retired.values():
        d_willgrowth.total_savings_retired += sav

    pc_ind2, _ = check_inputs_safe.safe_interp(d_nr['f_HEDI_to_pcInd'], HEDI_inc_life - d_willgrowth.total_savings)
    pc_ind_ret2, _ = check_inputs_safe.safe_interp(d_r['f_HEDI_to_pcInd'], HEDI_retired_inc_life - d_willgrowth.total_savings_retired)
    
    d_willgrowth.pc_individuals_without_enough_all_with_savings = (100 * pc_ind2 * d_nr['tot_individuals']
                                                  + 100 * pc_ind_ret2 * d_r['tot_individuals']) \
                                                  / (d_nr['tot_individuals'] + d_r['tot_individuals'])
    
    return d_common.__dict__, d_howmuch.__dict__, d_whohas.__dict__, d_dowe.__dict__, d_willgrowth.__dict__

def years_of_growth(total, annual_rate):
    # (1 + annual_rate) ** years_of_growth = 1 + total
    return np.log(1 + total)/np.log(1 + annual_rate)

def composition_to_equiv_factor (na, nc):
    return (ADULT1 + max(na-1, 0)*ADULT2 + nc*CHILD)

def equivalize(val, na, nc):
    return int(val * (composition_to_equiv_factor(2, 0)/composition_to_equiv_factor(na, nc)))

def dequivalize(val, na, nc):
    return int(val * (composition_to_equiv_factor(na, nc)/composition_to_equiv_factor(2, 0)))

def calc_disposable_income(income, retired=False):
    """
    subtract income tax and Class 1A employee contribution from income
    """
    income_remainder = income
    disposable_income = income

    #first calculate income tax
    for b, thresh in enumerate(INCOME_TAX_THRESHOLDS):

        if income_remainder > thresh:
            val_above = income_remainder - thresh
            disposable_income -= val_above * INCOME_TAX_RATES[b]
            income_remainder -= val_above

    if not retired:
        #now class 1A national insurance, employee contributions
        ni_remainder = income

        for b, thresh in enumerate(NI_THRESHOLDS):

            if ni_remainder >= thresh:
                val_above = ni_remainder - thresh
                disposable_income -= val_above * NI_RATES[b]
                ni_remainder -= val_above

    return disposable_income

incomes = [inc for inc in range(int(INCOME_TAX_THRESHOLDS_INV[2]), int(INCOME_TAX_THRESHOLDS_INV[0]), 1)]
incomes.insert(0, 0)
incomes.append(1000000)
calc_pre_tax_income = interp1d([calc_disposable_income(inc) for inc in incomes], incomes)
calc_pre_tax_income_retired = interp1d([calc_disposable_income(inc, True) for inc in incomes], 
                                       [inc + COUNCIL_TAX for inc in incomes])

def calc_pre_tax_income_pre_pension(disposable_income, pension_pc):
    
    pension = disposable_income * pension_pc/100

    pre_tax = pension + calc_pre_tax_income(disposable_income - pension + COUNCIL_TAX).item()    

    return pre_tax

def update_total_equivalized_spend(breakdown, savings_pc, pension_pc, retirement_pc):

    total_equivalized_spend=0
    
    for cat in breakdown:
        if (cat == 'Savings'):
            continue
        elif (cat == 'Pension'):
            continue
        elif (cat == 'Housing_deposit'):
            continue
        elif (cat == 'Childcare'):
            continue

        total_equivalized_spend +=  breakdown[cat]               
    
    #retirement quantity is % before savings, pension and lifetime contributions
    retirement_equivalized_spend = retirement_pc * total_equivalized_spend/100

    #saving pc is a pc of income not expense
    breakdown['Savings'] = total_equivalized_spend * (savings_pc/(100-savings_pc))
    total_equivalized_spend += breakdown['Savings']

    #pension pc is a pc of income not expense, including savings
    breakdown['Pension'] = total_equivalized_spend * (pension_pc/(100-pension_pc))
    total_equivalized_spend += breakdown['Pension']

    return total_equivalized_spend, retirement_equivalized_spend