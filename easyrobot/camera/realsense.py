'''
RealSense Camera.

Author: Hongjie Fang, Jirong Liu.
'''

import numpy as np
import pyrealsense2 as rs

from easyrobot.camera.base import CameraBase


class RealSenseCamera(CameraBase):
    '''
    RealSense Camera.
    '''
    def __init__(
        self, 
        serial, 
        frame_rate = 30, 
        resolution = (1280, 720),
        align = True,
        logger_name: str = "Camera",
        shm_name: str = "none", 
        streaming_freq: int = 30, 
        **kwargs
    ):
        '''
        Initialization.

        Parameters:
        - serial: str, required, the serial number of the realsense device;
        - frame_rate: int, optional, default: 15, the framerate of the realsense camera;
        - resolution: (int, int), optional, default: (1280, 720), the resolution of the realsense camera;
        - align: bool, optional, default: True, whether align the frameset with the RGB image;
        - logger_name: str, optional, default: "Camera", the name of the logger;
        - shm_name: str, optional, default: "none", the shared memory name of the camera data, "none" means no shared memory object;
        - streaming_freq: int, optional, default: 30, the streaming frequency.
        '''
        super(RealSenseCamera, self).__init__()
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.serial = serial
        # =============== Support L515 Camera ============== #
        self.is_radar = str.isalpha(serial[0])
        depth_resolution = (1024, 768) if self.is_radar else resolution
        if self.is_radar:
            frame_rate = max(frame_rate, 30)
            self.depth_scale = 4000
        else:
            self.depth_scale = 1000
        # ================================================== #
        self.config.enable_device(self.serial)
        self.config.enable_stream(rs.stream.depth, depth_resolution[0], depth_resolution[1], rs.format.z16, frame_rate)
        self.config.enable_stream(rs.stream.color, resolution[0], resolution[1], rs.format.rgb8, frame_rate)
        self.pipeline.start(self.config)
        self.align_to = rs.stream.color
        self.align = rs.align(self.align_to)
        self.with_align = align
        super(RealSenseCamera, self).__init__(
            logger_name = logger_name,
            shm_name = shm_name,
            streaming_freq = streaming_freq,
            **kwargs
        )

    def get_rgb_image(self):
        '''
        Get the RGB image from the camera.
        '''
        frames = self.pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        color_image = np.asanyarray(color_frame.get_data()).astype(np.float32)
        return color_image

    def get_depth_image(self):
        '''
        Get the depth image from the camera.
        '''
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        depth_image = np.asanyarray(depth_frame.get_data()).astype(np.float32) / self.depth_scale
        return depth_image

    def get_rgbd_image(self):
        '''
        Get the RGB image along with the depth image from the camera.
        '''
        frameset = self.pipeline.wait_for_frames()
        if self.with_align:
            frameset = self.align.process(frameset)
        color_image = np.asanyarray(frameset.get_color_frame().get_data()).astype(np.float32)
        depth_image = np.asanyarray(frameset.get_depth_frame().get_data()).astype(np.float32) / self.depth_scale
        return color_image, depth_image

    def get_info(self):         
        '''
        Get the data from camera (concatenated RGB-D image).
        '''
        frameset = self.pipeline.wait_for_frames()
        if self.with_align:
            frameset = self.align.process(frameset)
        color_image = np.asanyarray(frameset.get_color_frame().get_data()).astype(np.float32)
        depth_image = np.asanyarray(frameset.get_depth_frame().get_data()).astype(np.float32) / self.depth_scale
        depth_image_reshaped = np.expand_dims(depth_image, axis = 2)
        return np.concatenate((color_image, depth_image_reshaped), axis = -1)
