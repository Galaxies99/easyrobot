"""
Rotation utilities.

Authors: Hongjie Fang
"""

import torch
import functools
import numpy as np
import pytorch3d.transforms.rotation_conversions as ptc

from easyrobot.utils.transforms import rotation_utils as rtu


def rotation_transform(
    rot,
    from_rep, 
    to_rep, 
    from_convention = None, 
    to_convention = None
):
    """
    Transform a rotation representation into another equivalent rotation representation.
    """
    assert from_rep in rtu.VALID_ROTATION_REPRESENTATIONS, "Invalid rotation representation: {}".format(from_rep)
    assert to_rep in rtu.VALID_ROTATION_REPRESENTATIONS, "Invalid rotation representation: {}".format(to_rep)
    if from_rep == 'euler_angles':
        assert from_convention is not None
    else:
        from_convention = None
    if to_rep == 'euler_angles':
        assert to_convention is not None
    else:
        to_convention = None

    if from_rep == to_rep and from_convention == to_convention:
        return rot

    if from_rep != "matrix":
        if from_rep in ['rotation_9d', 'rotation_10d']:
            to_mat = getattr(rtu, "{}_to_matrix".format(from_rep))
        else:
            to_mat = getattr(ptc, "{}_to_matrix".format(from_rep))
            if from_convention is not None:
                to_mat = functools.partial(to_mat, convention = from_convention)
        mat = to_mat(torch.from_numpy(rot)).numpy()
    else:
        mat = rot
        
    if to_rep != "matrix":
        if to_rep in ['rotation_9d', 'rotation_10d']:
            to_ret = getattr(rtu, "matrix_to_{}".format(to_rep))
        else:
            to_ret = getattr(ptc, "matrix_to_{}".format(to_rep))
            if to_convention is not None:
                to_ret = functools.partial(to_ret, convention = to_convention)
        ret = to_ret(torch.from_numpy(mat)).numpy()
    else:
        ret = mat
    
    return ret

def rot_mat_x_axis(angle):
    """
    3x3 rotation matrix for rotation along x axis.
    """
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype = np.float32)

def rot_mat_y_axis(angle):
    """
    3x3 rotation matrix for rotation along y axis.
    """
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]], dtype = np.float32)

def rot_mat_z_axis(angle):
    """
    3x3 rotation matrix for rotation along z axis.
    """
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype = np.float32)

def rot_mat(angles):
    """
    3x3 rotation matrix for rotation along x, y, z axes.
    """
    x_mat = rot_mat_x_axis(angles[0])
    y_mat = rot_mat_y_axis(angles[1])
    z_mat = rot_mat_z_axis(angles[2])
    return z_mat @ y_mat @ x_mat
