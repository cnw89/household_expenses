import types
from helper_funcs import pc_str, salary_str, wage_str

MIN_WAGE = 10.5
DEFAULT_HOURS_PER_WEEK = 37.5
WEEKS_PER_YEAR = 52

def run(adult1, adult2, child, n_adults, n_children):

    #vars used for calculating in the javascript - passed via json.dumps()
    t = types.SimpleNamespace() 
    t.adult1 = adult1
    t.adult2 = adult2
    t.child = child
    t.n_adults = n_adults
    t.n_children = n_children
    
    t.min_wage = MIN_WAGE
    t.default_hours_per_week = DEFAULT_HOURS_PER_WEEK
    t.weeks_per_year = WEEKS_PER_YEAR

    #make some dummy results
    #vars for calculting here, unchanging in results page
    s = types.SimpleNamespace() 
    s.min_wage = MIN_WAGE
    s.default_hours_per_week = DEFAULT_HOURS_PER_WEEK
    s.weeks_per_year = WEEKS_PER_YEAR

    #FROM HERE...
    s.total = adult1 + (n_adults-1)*adult2 + n_children * child    
    s.one_adult_salary = 1.4 * s.total
    s.two_adult_salary = 0.65 * s.total

    s.one_adult_hours_per_week = s.one_adult_salary/(MIN_WAGE * WEEKS_PER_YEAR)
    s.two_adult_hours_per_week = s.two_adult_salary/(MIN_WAGE * WEEKS_PER_YEAR)

    s.one_adult_hours_greater_than_default = (s.one_adult_hours_per_week > DEFAULT_HOURS_PER_WEEK)
    s.two_adult_hours_greater_than_default = (s.two_adult_hours_per_week > DEFAULT_HOURS_PER_WEEK)

    s.one_adult_wage_at_default_hours = s.one_adult_salary/(DEFAULT_HOURS_PER_WEEK * WEEKS_PER_YEAR)
    s.two_adult_wage_at_default_hours = s.two_adult_salary/(DEFAULT_HOURS_PER_WEEK * WEEKS_PER_YEAR)
    #UNTIL HERE - just calculate in javascript to be adaptable to household composition

    s.pc_households_with_enough = s.two_adult_salary/100000
    s.pc_enough_of_bottom_10 = 20000/s.two_adult_salary
    s.pc_enough_of_median = 28000/s.two_adult_salary
    s.pc_enough_of_top_10 = 60000/s.two_adult_salary
    s.pc_enough_of_top_1 = 120000/s.two_adult_salary

    s.pc_everyone_household_earnings = s.two_adult_salary/35000
    s.pc_everyone_gdp = 0.6*s.two_adult_salary/35000

    s.pc_growth_even = 1 - s.pc_enough_of_bottom_10
    s.growth_even_years = s.pc_growth_even/2
    s.pc_growth_uneven = 1.5 * s.pc_growth_even  
    s.growth_uneven_years= s.pc_growth_uneven/2

    sout = s.__dict__
    tout = t.__dict__
    # for key in out:
    #     if 'pc' in key:
    #         out[key + '_s'] = pc_str(out[key])
    #     elif 'salary' in key:
    #         out[key +'_s'] = salary_str(out[key])
    #     elif 'wage'

    return sout, tout