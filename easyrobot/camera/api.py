'''
Camera API.

Author: Hongjie Fang.
'''

import re
from easyrobot.camera.base import CameraBase
from easyrobot.camera.realsense import RealSenseCamera


def get_camera(**params):
    '''
    Get the camera object from the camera library.
    '''
    name = params.get('name', 'none')
    try:
        if re.fullmatch('[ -_]*realsense[ -_]*', str.lower(name)):
            return RealSenseCamera(**params)
        else:
            return CameraBase(**params)
    except Exception:
        return CameraBase(**params)
