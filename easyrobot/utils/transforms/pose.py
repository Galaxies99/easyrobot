"""
Pose utilities.

Authors: Hongjie Fang
"""

import numpy as np

from easyrobot.utils.transforms import rotation as rt
from easyrobot.utils.transforms import rotation_utils as rtu


def xyz_rot_transform(
    xyz_rot,
    from_rep, 
    to_rep, 
    from_convention = None, 
    to_convention = None
):
    """
    Transform an xyz_rot representation into another equivalent xyz_rot representation.
    """
    assert from_rep in rtu.VALID_ROTATION_REPRESENTATIONS, "Invalid rotation representation: {}".format(from_rep)
    assert to_rep in rtu.VALID_ROTATION_REPRESENTATIONS, "Invalid rotation representation: {}".format(to_rep)

    if from_rep == to_rep and from_convention == to_convention:
        return xyz_rot

    xyz_rot = np.array(xyz_rot)
    if from_rep != "matrix":
        assert xyz_rot.shape[-1] == 3 + rtu.ROTATION_REPRESENTATION_DIMS[from_rep]
        xyz = xyz_rot[..., :3]
        rot = xyz_rot[..., 3:]
    else:
        assert xyz_rot.shape[-1] == 4 and xyz_rot.shape[-2] == 4
        xyz = xyz_rot[..., :3, 3]
        rot = xyz_rot[..., :3, :3]
    rot = rt.rotation_transform(
        rot = rot,
        from_rep = from_rep,
        to_rep = to_rep,
        from_convention = from_convention,
        to_convention = to_convention
    )
    if to_rep != "matrix":
        return np.concatenate((xyz, rot), axis = -1)
    else:
        res = np.zeros(xyz.shape[:-1] + (4, 4), dtype = np.float32)
        res[..., :3, :3] = rot
        res[..., :3, 3] = xyz
        res[..., 3, 3] = 1
        return res


def xyz_rot_to_mat(xyz_rot, rotation_rep, rotation_rep_convention = None):
    """
    Transform an xyz_rot representation under any rotation form to an unified 4x4 pose representation.
    """
    return xyz_rot_transform(
        xyz_rot,
        from_rep = rotation_rep,
        to_rep = "matrix",
        from_convention = rotation_rep_convention
    )


def mat_to_xyz_rot(mat, rotation_rep, rotation_rep_convention = None):
    """
    Transform an unified 4x4 pose representation to an xyz_rot representation under any rotation form.
    """
    return xyz_rot_transform(
        mat,
        from_rep = "matrix",
        to_rep = rotation_rep,
        to_convention = rotation_rep_convention
    )


def construct_pose(xyz, rot, from_rep, to_rep, from_convention = None, to_convention = None):
    """
    Construct pose from xyz and rotation.
    """
    rot = rt.rotation_transform(
        rot,
        from_rep = from_rep,
        to_rep = to_rep,
        from_convention = from_convention,
        to_convention = to_convention
    )
    if to_rep == "matrix":
        assert xyz.shape[:-1] == rot.shape[:-2], "Imcompatible shape between xyz and rotation."
        pose = np.zeros(xyz.shape[:-1] + (4, 4), dtype = np.float32)
        pose[..., :3, 3] = xyz
        pose[..., :3, :3] = rot
        pose[..., 3, 3] = 1.0
        return pose
    else:
        assert xyz.shape[:-1] == rot.shape[:-1], "Imcompatible shape between xyz and rotation."
        return np.concatenate([xyz, rot], axis = -1)


def apply_mat_to_pose(pose, mat, rotation_rep, rotation_rep_convention = None):
    """
    Apply transformation matrix mat to pose under any rotation form.
    """
    assert rotation_rep in rtu.VALID_ROTATION_REPRESENTATIONS, "Invalid rotation representation: {}".format(rotation_rep)
    mat = np.array(mat)
    pose = np.array(pose)
    assert mat.shape == (4, 4)
    if rotation_rep == "matrix":
        assert pose.shape[-2] == 4 and pose.shape[-1] == 4
        res_pose = mat @ pose
        return res_pose
    assert pose.shape[-1] == 3 + rtu.ROTATION_REPRESENTATION_DIMS[rotation_rep]
    pose_mat = xyz_rot_to_mat(
        xyz_rot = pose,
        rotation_rep = rotation_rep,
        rotation_rep_convention = rotation_rep_convention
    )
    res_pose_mat = mat @ pose_mat
    res_pose = mat_to_xyz_rot(
        mat = res_pose_mat,
        rotation_rep = rotation_rep,
        rotation_rep_convention = rotation_rep_convention
    )
    return res_pose


def apply_mat_to_pcd(pcd, mat):
    """
    Apply transformation matrix mat to point cloud.
    """
    mat = np.array(mat)
    assert mat.shape == (4, 4)
    pcd[..., :3] = (mat[:3, :3] @ pcd[..., :3].T).T + mat[:3, 3]
    return pcd


def trans_mat(offsets):
    """
    4x4 transformation matrix for translation along x, y, z axes.
    """
    res = np.identity(4, dtype = np.float32)
    res[:3, 3] = np.array(offsets)
    return res

def rot_trans_mat(offsets, angles):
    """
    4x4 transformation matrix for rotation along x, y, z axes, then translation along x, y, z axes.
    """
    res = np.identity(4, dtype = np.float32)
    res[:3, :3] = rt.rot_mat(angles)
    res[:3, 3] = np.array(offsets)
    return res

def trans_rot_mat(offsets, angles):
    """
    4x4 transformation matrix for translation along x, y, z axes, then rotation along x, y, z axes.
    """
    res = np.identity(4, dtype = np.float32)
    res[:3, :3] = rt.rot_mat(angles)
    offsets = (res[:3, :3] @ np.array(offsets).unsqueeze(-1)).squeeze()
    res[:3, 3] = offsets
    return res