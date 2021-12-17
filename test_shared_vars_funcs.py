""" test utility functions from shared_vars_func.py"""
from shared_vars_funcs import hhmmss_to_seconds
from shared_vars_funcs import time_delay
from shared_vars_funcs import dict2list

def test_hhmmss_to_seconds():
    """ tests function with 4 different inputs"""

    assert hhmmss_to_seconds('16:45:32') == 60_332
    assert hhmmss_to_seconds('12:00') == 43_200
    assert hhmmss_to_seconds('6:23') == 22_980
    assert hhmmss_to_seconds('00:00:11') == 11

def test_time_delay():
    """ tests function with 5 different inputs"""

    # the functions use is such that the second argument only needs
    # to be of the form hh:mm
    assert time_delay('12:00', '13:00') == 3_600
    assert time_delay('13:00', '12:00') == 82_800
    assert time_delay('23:23:23', '18:16') == 67_957
    assert time_delay('20:44:01', '20:45') == 59
    assert time_delay('10:37', '10:36:59') == 86399

def test_dict2list():
    """ Creates a dictionary and passes it into the function and checks output"""
    test_dictionary ={
        1: {'test': 'test', 'd':'d'},
        2: 12,
        3: 'string',
        4: [1,2,3],
        5: 'number'
        }
    output_list = dict2list(test_dictionary)
    assert isinstance(output_list, list)
    for key, value in test_dictionary.items():
        assert value == output_list[key-1]
