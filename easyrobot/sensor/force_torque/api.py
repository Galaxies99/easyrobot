'''
Force/Torque Sensor API.

Author: Hongjie Fang.
'''

import re
from easyrobot.sensor.force_torque.ati import ATIFTSensor
from easyrobot.sensor.force_torque.base import FTSensorBase
from easyrobot.sensor.force_torque.optoforce import OptoForceFTSensor


def get_force_torque_sensor(**params):
    '''
    Get the force/torque sensor object from the force/torque sensor library.
    '''
    name = params.get('name', None)
    if name is not None:
        del params['name']
    try:
        if re.fullmatch('[ -_]*ati[ -_]*', str.lower(name)):
            return ATIFTSensor(**params)
        elif re.fullmatch('[ -_]*optoforce[ -_]*', str.lower(name)):
            return OptoForceFTSensor(**params)
        else:
            return FTSensorBase(**params)
    except Exception:
        return FTSensorBase(**params)