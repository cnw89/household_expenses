import json
import hashlib

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
