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
    #vars directly injected into html with Jinja

    # common variables for use in the text
    d_common = types.SimpleNamespace() 
    d_common.min_wage = MIN_WAGE
    d_common.default_hours_per_week = DEFAULT_HOURS_PER_WEEK
    
    d_common.first_adult = equivalize(HEDI, 1, 0)
    d_common.second_adult = equivalize(HEDI, 2, 0) - equivalize(HEDI, 1, 0)
    d_common.child = equivalize(HEDI, 1, 1) - equivalize(HEDI, 1, 0)

    #other variables organised by infographic
    #1 how much is enough
    d_howmuch = types.SimpleNamespace()  
    adults = [1, 1, 2, 2, 2, 2]
    children = [0, 1, 0, 1, 2, 3]
    d_howmuch.base = [dequivalize(HEDI, na, nc) for (na, nc) in zip(adults, children)]
    d_howmuch.with_tax1 = [calc_with_tax(sal, 1) for sal in d_howmuch.base]
    d_howmuch.with_tax2 = [calc_with_tax(sal, 2) for sal in d_howmuch.base]

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
    d_dowe.deficit_without_enough = d['f_pcInd_to_deficit_below'](pc_ind).item()
    print(d_dowe.uk_gdhi)
    print(d_dowe.enough_for_everyone)
    print(d_dowe.deficit_without_enough)    

    #4 will growth
    d_willgrowth = types.SimpleNamespace() 
 
    #Now things that won't be updated in html:    
    """
    s.pc_enough_of_bottom_10 = d['f_pcInd_to_HEDI'](0.05)/HEDI #check should this be 0.1
    s.pc_enough_of_median =  d['f_pcInd_to_HEDI'](0.5)/HEDI
    s.pc_enough_of_top_10 = d['f_pcInd_to_HEDI'](0.95)/HEDI #check should this be 0.9
    s.pc_enough_of_top_1 =  d['f_pcInd_to_HEDI'](0.995)/HEDI #PLACEHOLDER - need more data for 1%

    s.pc_enough_gdhi = 100 * d['f_pcInd_to_required_incomesum'](pc_ind)/UK_GDHI
    s.pc_deficit_gdhi = 100 * d['f_pcInd_to_deficit_below'](pc_ind)/UK_GDHI
    s.pc_excess_gdhi = 100 - s.pc_enough_gdhi #100 * d['f_pcInd_to_excess_above'](pc_ind)/UK_GDHI
    s.uk_gdhi = UK_GDHI

    s.pc_growth = 100 * (1 / s.pc_enough_of_bottom_10 - 1)
    s.growth_even_years = years_of_growth(s.pc_growth/100, UK_ANNUAL_GROWTH)
    s.growth_uneven_years= years_of_growth(s.pc_growth/100, UK_ANNUAL_GROWTH * UK_LOWEST_DECILE_GROWTH_SHARE)
    s.annual_growth_even = 100 * UK_ANNUAL_GROWTH
    s.annual_growth_uneven = 100 * UK_ANNUAL_GROWTH * UK_LOWEST_DECILE_GROWTH_SHARE

    """
    

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

def calc_with_tax(val, n_earners):

 return 1.3*val