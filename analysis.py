import types
import pickle
from scipy.interpolate import interp1d
import numpy as np


filename = 'income_assessment.pickle'
with open(filename, 'rb') as fID:
    d = pickle.load(fID)

#dict_keys(['f_HEDI_to_pcInd', 'f_pcInd_to_HEDI', 'tot_households', 'f_pcInd_to_pcHouse', 
# 'f_pcInd_to_pcHouse_byComp', 'd_household_comps_to_index', 'f_pcInd_to_required_incomesum', 
# 'f_pcInd_to_deficit_below', 'f_pcInd_to_excess_above'])

MIN_WAGE = 10.5
DEFAULT_HOURS_PER_WEEK = 37.5
WEEKS_PER_YEAR = 52

#equivalization factors from OECD-modified standard:
ADULT1 = 1
ADULT2 = 0.5
CHILD = 0.3

UK_GDHI = 1438237*1e6
UK_ANNUAL_GROWTH = 0.015
UK_LOWEST_DECILE_GROWTH_SHARE = 0.75

def run(HEDI):
    """
    HEDI - household equivalized disposable income - equivalized to 2 adults, 0 children. 
    """
    
    #vars used for calculating in the javascript - passed via json.dumps()
    t = types.SimpleNamespace() 
    t.HEDI = HEDI
    #equivalization factors from OECD-modified standard:
    t.adult1 = ADULT1
    t.adult2 = ADULT2
    t.child = CHILD
    
    t.min_wage = MIN_WAGE
    t.default_hours_per_week = DEFAULT_HOURS_PER_WEEK
    t.weeks_per_year = WEEKS_PER_YEAR

    t.household_comps = list(d['d_household_comps_to_index'].keys())

    #vars directly injected into html with Jinja
    s = types.SimpleNamespace() 
    s.min_wage = MIN_WAGE
    s.default_hours_per_week = DEFAULT_HOURS_PER_WEEK
    s.weeks_per_year = WEEKS_PER_YEAR

    #FROM HERE... placeholders only - calculate in javascript to be adaptable to household composition
    s.total = 0   
    s.one_adult_salary = 0
    s.two_adult_salary = 0

    s.one_adult_hours_per_week = 0
    s.two_adult_hours_per_week = 0

    s.one_adult_hours_greater_than_default = False
    s.two_adult_hours_greater_than_default = False

    s.one_adult_wage_at_default_hours = 0
    s.two_adult_wage_at_default_hours = 0
    #TO HERE

    #Now things that won't be updated in html:
    pc_ind = d['f_HEDI_to_pcInd'](HEDI)
    s.pc_individuals_with_enough = 100 * pc_ind
    s.pc_households_with_enough = 100 * d['f_pcInd_to_pcHouse'](pc_ind)
    s.pc_enough_of_bottom_10 = d['f_pcInd_to_HEDI'](0.05)/HEDI #check should this be 0.1
    s.pc_enough_of_median =  d['f_pcInd_to_HEDI'](0.5)/HEDI
    s.pc_enough_of_top_10 = d['f_pcInd_to_HEDI'](0.95)/HEDI #check should this be 0.9
    s.pc_enough_of_top_1 =  d['f_pcInd_to_HEDI'](0.995)/HEDI #PLACEHOLDER - need more data for 1%

    s.pc_enough_gdhi = 100 * d['f_pcInd_to_required_incomesum'](pc_ind)/UK_GDHI
    s.pc_deficit_gdhi = 100 * d['f_pcInd_to_deficit_below'](pc_ind)/UK_GDHI
    s.pc_excess_gdhi = 100 * d['f_pcInd_to_excess_above'](pc_ind)/UK_GDHI
    s.uk_gdhi = UK_GDHI

    s.pc_growth = 100 * (1 / s.pc_enough_of_bottom_10 - 1)
    s.growth_even_years = years_of_growth(s.pc_growth/100, UK_ANNUAL_GROWTH)
    s.growth_uneven_years= years_of_growth(s.pc_growth/100, UK_ANNUAL_GROWTH * UK_LOWEST_DECILE_GROWTH_SHARE)
    s.annual_growth_even = 100 * UK_ANNUAL_GROWTH
    s.annual_growth_uneven = 100 * UK_ANNUAL_GROWTH * UK_LOWEST_DECILE_GROWTH_SHARE

    sout = s.__dict__
    tout = t.__dict__

    return sout, tout

def years_of_growth(total, annual_rate):
    # (1 + annual_rate) ** years_of_growth = 1 + total
    return np.log(1 + total)/np.log(1 + annual_rate)

def composition_to_equiv_factor (na, nc):
    return (ADULT1 + max(na-1, 0)*ADULT2 + nc*CHILD)

def equivalize(val, na, nc):
    return int(val * (composition_to_equiv_factor(2, 0)/composition_to_equiv_factor(na, nc)))

def dequivalize(val, na, nc):
    return int(val * (composition_to_equiv_factor(na, nc)/composition_to_equiv_factor(2, 0)))