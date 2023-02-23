
def run(HEDI, 
        breakdown, 
        lifetime_breakdown, 
        pension_pc, 
        HEDI_retired, 
        n_adults, 
        n_children,
        d_r,
        d_nr):

    
    #first sanity check HEDI 
    pc_ind = d_nr['f_HEDI_to_pcInd'](HEDI).item() # the percentile individual who has this household equivalized disposable income
    warn_user = False
    warn_text = ''

    if pc_ind < 0:
        pc_ind = 0.05
        HEDI = d_nr['f_pcInd_to_HEDI'](pc_ind).item()
        warn_user = True
        warn_text = "Sorry, the expense budget you've defined is out of range for this app's analysis (too low)! \
                    We have replaced it with a budget that corresponds to the 5th percentile \
                    household disposable income for two adults.\n"
        #also do for retired:
        pc_ind_ret = 0.05
        HEDI_retired = d_r['f_pcInd_to_HEDI'](pc_ind_ret).item()

    elif pc_ind > 1:
        pc_ind = 0.95
        HEDI = d_nr['f_pcInd_to_HEDI'](pc_ind).item()
        warn_user = True
        warn_text = "Sorry, the expense budget you've defined is out of range for this app's analysis (too high)! \
                    We have replaced it with a budget that corresponds to the 95th percentile \
                    household disposable income for two adults.\n"

        #also do for retired:
        pc_ind_ret = 0.95
        HEDI_retired = d_r['f_pcInd_to_HEDI'](pc_ind_ret).item()
    
    elif pc_ind < 0.05:
        warn_user = True
        warn_text = "The expense budget you've defined is quite low. \
                     Please be aware that this means that the percentage of people who have enough, described below, is likely to be inaccurate.\n"
    
    elif pc_ind > 0.95:
        warn_user = True
        warn_text = "The expense budget you've defined is quite high. \
                     Please be aware that this means that the percentage of people who have enough, described below, is likely to be inaccurate.\n"
        
    # now do the same for HEDI_retired
    pc_ind_ret = d_r['f_HEDI_to_pcInd'](HEDI_retired).item() # the percentile individual who has this household equivalized disposable income
    
    if pc_ind_ret < 0:
        pc_ind_ret = 0.05
        HEDI_retired = d_r['f_pcInd_to_HEDI'](pc_ind_ret).item()
        warn_user = True
        warn_text += "Sorry, the expense budget you've defined for retirement is out of range for this app's analysis (too low)! \
                    We have replaced it with a budget that corresponds to the 5th percentile \
                    household disposable income for two retired adults.\n"
    elif pc_ind_ret > 1:
        pc_ind_ret = 0.95
        HEDI_retired = d_r['f_pcInd_to_HEDI'](pc_ind_ret).item()
        warn_user = True
        warn_text += "Sorry, the expense budget you've defined for retirement is out of range for this app's analysis (too high)! \
                    We have replaced it with a budget that corresponds to the 95th percentile \
                    household disposable income for two retired adults.\n"
            
    elif pc_ind_ret < 0.05:
        warn_user = True
        warn_text += "The expense budget you've defined for retirement is quite low. \
                     Please be aware that this means that the percentage of people who have enough, described below, is likely to be inaccurate.\n"
    
    elif pc_ind_ret > 0.95:
        warn_user = True
        warn_text += "The expense budget you've defined for retirement is quite high. \
                     Please be aware that this means that the percentage of people who have enough, described below, is likely to be inaccurate.\n"
        
    return HEDI, breakdown, lifetime_breakdown, pension_pc, HEDI_retired, n_adults, n_children, warn_user, warn_text