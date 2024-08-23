'''
Gripper API.

Author: Hongjie Fang.
'''

import re
from easyrobot.gripper.base import GripperBase
from easyrobot.gripper.virtual import VirtualGripper
from easyrobot.gripper.robotiq import Robotiq2FGripper
from easyrobot.gripper.dahuan import DahuanAG95Gripper


def get_gripper(**params):
    '''
    Get the gripper object from the gripper library.
    '''
    name = params.get('name', None)
    if name is not None:
        del params['name']
    try:
        if re.fullmatch('[ -_]*virtual[ -_]*', str.lower(name)):
            return VirtualGripper(**params)
        elif re.fullmatch('[ -_]*robotiq[ -_]*2f[ -_]*(85|140)[ -_]*', str.lower(name)):
            return Robotiq2FGripper(**params)
        elif re.fullmatch('[ -_]*dahuan[ -_]*ag[ -_]*95[ -_]*', str.lower(name)):
            return DahuanAG95Gripper(**params)
        else:
            return GripperBase(**params)
    except Exception:
        return GripperBase(**params)