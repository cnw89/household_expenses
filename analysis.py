import types
import pickle
import numpy as np
from scipy.interpolate import interp1d
import copy

from pathlib import Path
THIS_FOLDER = Path(__file__).parent.resolve()

filename = THIS_FOLDER / "income_assessment.pickle"

with open(filename, 'rb') as fID:
    d = pickle.load(fID)

#dict_keys(['f_HEDI_to_pcInd', 'f_pcInd_to_HEDI', 'tot_households', 'f_pcInd_to_pcHouse',
# 'f_pcInd_to_pcHouse_byComp', 'd_household_comps_to_index', 'f_pcInd_to_required_incomesum',
# 'f_pcInd_to_deficit_below', 'f_pcInd_to_excess_above'])

MIN_WAGE = 10.42
DEFAULT_HOURS_PER_WEEK = 37.5

#equivalization factors from OECD-modified standard:
ADULT1 = 1
ADULT2 = 0.5
CHILD = 0.3

UK_GDHI = 1438237*1e6
UK_ANNUAL_GROWTH = 0.015
UK_LOWEST_DECILE_GROWTH_SHARE = 0.75

#checked January 2023
INCOME_TAX_THRESHOLDS = [150000, 50270, 12570] #annual salary thresholds
INCOME_TAX_RATES = [0.45, 0.4, 0.2]

thresh1 = (INCOME_TAX_THRESHOLDS[1] - INCOME_TAX_THRESHOLDS[2])*(1 - INCOME_TAX_RATES[2]) + INCOME_TAX_THRESHOLDS[2]
thresh2 = (INCOME_TAX_THRESHOLDS[0] - INCOME_TAX_THRESHOLDS[1])*(1 - INCOME_TAX_RATES[1]) + thresh1
INCOME_TAX_THRESHOLDS_INV = [thresh2, thresh1, INCOME_TAX_THRESHOLDS[2]]

#Class 1A national insurance, employee contributions, valid to April 2023
NI_THRESHOLDS = [967, 242.01] #weekly earnings thresholds
NI_RATES = [0.02, 0.12]

COUNCIL_TAX = 1600

thresh1 = (NI_THRESHOLDS[0] - NI_THRESHOLDS[1])*(1 - NI_RATES[1]) + NI_THRESHOLDS[1]
NI_THRESHOLDS_INV = [thresh1, NI_THRESHOLDS[1]]

EMPLOYER_PENSION_CONTRIB_PC = 3
AVERAGE_CHILDREN_PER_HOUSE = 0.8
NON_RETIRED_HOUSEHOLD_YEARS = 40
SAVE_FOR_FIRST_HOUSE_YEARS = 7

def run(HEDI, breakdown, lifetime_breakdown, pension_pc, n_adults, n_children):
    """
    HEDI - household equivalized disposable income - equivalized to 2 adults, 0 children.
    """
    #vars directly injected into html with Jinja

    # common variables for use in the text
    d_common = types.SimpleNamespace()
    d_common.min_wage = MIN_WAGE
    d_common.default_hours_per_week = DEFAULT_HOURS_PER_WEEK
    d_common.employer_pension_contrib_pc = EMPLOYER_PENSION_CONTRIB_PC
    d_common.council_tax = COUNCIL_TAX
    d_common.average_children_per_house = AVERAGE_CHILDREN_PER_HOUSE 
    d_common.non_retired_household_years = NON_RETIRED_HOUSEHOLD_YEARS 
    
    #monthly
    d_common.first_adult = dequivalize(HEDI, 1, 0)/12
    d_common.second_adult = (dequivalize(HEDI, 2, 0) - dequivalize(HEDI, 1, 0))/12
    d_common.child = (dequivalize(HEDI, 1, 1) - dequivalize(HEDI, 1, 0))/12

    #personalized for the respondant
    d_common.n_adults = n_adults
    d_common.n_children = n_children
    d_common.base = dequivalize(HEDI, n_adults, n_children)
    d_common.with_tax1 = calc_pre_tax_income_pre_pension((d_common.base + COUNCIL_TAX), pension_pc)
    d_common.with_tax2 = calc_pre_tax_income_pre_pension((d_common.base + COUNCIL_TAX)/2, pension_pc)
    d_common.hours_1 = d_common.with_tax1/(MIN_WAGE * 52)
    d_common.hours_2 = d_common.with_tax2/(MIN_WAGE * 52)
    # d_common.is_long_hours_1 = d_common.hours_1 > DEFAULT_HOURS_PER_WEEK
    # d_common.is_long_hours_2 = d_common.hours_2 > DEFAULT_HOURS_PER_WEEK
    d_common.wage_1 = d_common.with_tax1/(DEFAULT_HOURS_PER_WEEK * 52)
    d_common.wage_2 = d_common.with_tax2/(DEFAULT_HOURS_PER_WEEK * 52)

    #other variables organised by infographic
    #1 how much is enough
    d_howmuch = types.SimpleNamespace()
    adults = [1, 1, 2, 2, 2, 2]
    children = [0, 1, 0, 1, 2, 3]
    d_howmuch.base = [dequivalize(HEDI, na, nc) for (na, nc) in zip(adults, children)]
    d_howmuch.with_tax1 = [calc_pre_tax_income_pre_pension((sal + COUNCIL_TAX), pension_pc) for sal in d_howmuch.base]
    d_howmuch.with_tax2 = [calc_pre_tax_income_pre_pension((sal + COUNCIL_TAX)/min(2, na), pension_pc) for sal, na in zip(d_howmuch.base, adults)]

    d_howmuch.save_for_first_house_years = SAVE_FOR_FIRST_HOUSE_YEARS
    d_howmuch.while_saving_for_first_house = (lifetime_breakdown['House_deposit']/SAVE_FOR_FIRST_HOUSE_YEARS) - dequivalize(breakdown['House_deposit'], n_adults, n_children)
    d_howmuch.while_preschool_childcare = lifetime_breakdown['Childcare'] - dequivalize(breakdown['Childcare'], n_adults, n_children)

    #what does it take to earn enough calculated in browser from how much is enough...

    #2 who has enough
    d_whohas = types.SimpleNamespace()
    pc_ind = d['f_HEDI_to_pcInd'](HEDI) # the percentile individual who has this household equivalized disposable income
    d_whohas.pc_individuals_without_enough = 100 * pc_ind
    d_whohas.pc_households_without_enough = 100 * d['f_pcInd_to_pcHouse'](pc_ind).item()
    d_whohas.pc_enough_by_decile = [dec/HEDI for dec in d['l_deciles_av'] ]

    #3 do we have enough
    d_dowe = types.SimpleNamespace()
    d_dowe.uk_gdhi = UK_GDHI
    d_dowe.enough_for_everyone = d['f_pcInd_to_required_incomesum'](pc_ind).item()
    d_dowe.enough_for_everyone_ratio = d_dowe.enough_for_everyone/UK_GDHI
    d_dowe.deficit_without_enough = d['f_pcInd_to_deficit_below'](pc_ind).item()
    d_dowe.deficit_without_enough_ratio = d_dowe.deficit_without_enough/UK_GDHI

    #4 will growth
    d_willgrowth = types.SimpleNamespace() 
    d_willgrowth.years = [1977, 2021]
    d_willgrowth.growth_bottom = 1.5
    d_willgrowth.growth_top = 2.2
    d_willgrowth.growth_UK = 1.9
    d_willgrowth.bottom_growth_to_enough = 100 * (1/d_whohas.pc_enough_by_decile[0] - 1)
    d_willgrowth.bottom_years_to_enough = years_of_growth(d_willgrowth.bottom_growth_to_enough/100, d_willgrowth.growth_bottom/100)

    #find fraction of wealth over a multiple of enough, which is 
    tax_thresh_ratio = min(3, np.floor(d_whohas.pc_enough_by_decile[-1]))
    if tax_thresh_ratio > 1:
        pc_ind_tax_thresh = d['f_HEDI_to_pcInd'](HEDI * tax_thresh_ratio)
        excess_over_tax_thresh = d['f_pcInd_to_excess_above'](pc_ind_tax_thresh)

        while (excess_over_tax_thresh < d_dowe.deficit_without_enough) and (tax_thresh_ratio > 1):
            tax_thresh_ratio -= 1
            pc_ind_tax_thresh = d['f_HEDI_to_pcInd'](HEDI * tax_thresh_ratio)
            excess_over_tax_thresh = d['f_pcInd_to_excess_above'](pc_ind_tax_thresh)

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

def calc_disposable_income(income):
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

    #now class 1A national insurance, employee contributions
    ni_remainder = income/52

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

def calc_pre_tax_income_pre_pension(disposable_income, pension_pc):

    after_employee_pension_contrib = calc_pre_tax_income(disposable_income * (1 - pension_pc/100)).item()
    before_employee_pension_contrib = after_employee_pension_contrib/(1- (pension_pc - EMPLOYER_PENSION_CONTRIB_PC)/100)

    return before_employee_pension_contrib