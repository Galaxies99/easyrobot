'''
Force/Torque Sensor API.

Author: Hongjie Fang.
'''

import re
from easyrobot.ftsensor.ati import ATIFTSensor
from easyrobot.ftsensor.base import FTSensorBase
from easyrobot.ftsensor.optoforce import OptoForceFTSensor


def get_ftsensor(**params):
    '''
    Get the force/torque sensor object from the force/torque sensor library.
    '''
    name = params.get('name', None)
    try:
        if re.fullmatch('[ -_]*ati[ -_]*', str.lower(name)):
            return ATIFTSensor(**params)
        elif re.fullmatch('[ -_]*optoforce[ -_]*', str.lower(name)):
            return OptoForceFTSensor(**params)
        else:
            return FTSensorBase(**params)
    except Exception:
        return FTSensorBase(**params)