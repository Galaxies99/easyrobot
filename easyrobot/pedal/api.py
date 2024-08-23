'''
Pedal API.

Author: Hongjie Fang.
'''

import re
from easyrobot.pedal.base import PedalBase
from easyrobot.pedal.logitech import LogitechG29Pedal


def get_pedal(**params):
    '''
    Get the pedal object from the pedal library.
    '''
    name = params.get('name', None)
    if name is not None:
        del params['name']
    try:
        if re.fullmatch('[ -_]*logitech[ -_]*g29[ -_]*', str.lower(name)):
            return LogitechG29Pedal(**params)
        else:
            return PedalBase(**params)
    except Exception:
        return PedalBase(**params)