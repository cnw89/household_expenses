import json
import hashlib
import math

def dict_hash(dictionary):
    """MD5 hash of a dictionary."""
    dhash = hashlib.md5()
    # We need to sort arguments so {'a': 1, 'b': 2} is
    # the same as {'b': 2, 'a': 1}
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()

def freq_text_to_int(freqstr):

    if freqstr == 'month':
        return 12
    elif freqstr == 'week':
        return 52
    elif freqstr == 'day':
        return 365
    else:
        return 1

def salary_str(val):

    return f'£{int(val):,}'

def wage_str(val):

    return f'£{math.round(val, 2):,}'

def pc_str(val):
    
    return f'{int(100*val)}%'
