'''
Robot API.

Author: Hongjie Fang.
'''

import re
from easyrobot.robot.base import RobotBase
from easyrobot.robot.flexiv import FlexivRobot


def get_robot(**params):
    '''
    Get the robot object from the robot library.
    '''
    name = params.get('name', None)
    try:
        if re.fullmatch('[ -_]*flexiv[ -_]*', str.lower(name)):
            return FlexivRobot(**params)
        else:
            return RobotBase(**params)
    except Exception:
        return RobotBase(**params)
