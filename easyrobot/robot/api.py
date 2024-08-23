'''
Robot API.

Author: Hongjie Fang.
'''

import re
from easyrobot.robot.base import RobotBase
from easyrobot.robot.flexiv import FlexivRobot
from easyrobot.robot.virtual import VirtualRobot


def get_robot(**params):
    '''
    Get the robot object from the robot library.
    '''
    name = params.get('name', None)
    if name is not None:
        del params['name']
    try:
        if re.fullmatch('[ -_]*virtual[ -_]*', str.lower(name)):
            return VirtualRobot(**params)
        elif re.fullmatch('[ -_]*flexiv[ -_]*', str.lower(name)):
            return FlexivRobot(**params)
        else:
            return RobotBase(**params)
    except Exception:
        return RobotBase(**params)
