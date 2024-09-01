'''
Camera Base Interface.

Author: Hongjie Fang.
'''

import time
import logging
import threading
import numpy as np

from easyrobot.utils.logger import ColoredLogger
from easyrobot.utils.shared_memory import SharedMemoryManager


class RGBCameraBase(object):
    def __init__(
        self, 
        logger_name: str = "RGB Camera",
        shm_name: str = None, 
        streaming_freq: int = 30, 
        **kwargs
    ): 
        '''
        Initialization.
        
        Parameters:
        - logger_name: str, optional, default: "RGBCamera", the name of the logger;
        - shm_name: str, optional, default: None, the shared memory name of the camera data, None means no shared memory object;
        - streaming_freq: int, optional, default: 30, the streaming frequency.
        '''
        super(RGBCameraBase, self).__init__()
        logging.setLoggerClass(ColoredLogger)
        self.logger = logging.getLogger(logger_name)
        self.is_streaming = False
        self.with_streaming = (shm_name is not None)
        self.streaming_freq = streaming_freq
        self.shm_name = shm_name
        self._prepare_shm()

    def _prepare_shm(self):
        '''
        Prepare shared memory objects.
        '''
        if self.with_streaming:
            info = np.array(self.get_info()).astype(np.uint8)
            self.shm_camera = SharedMemoryManager(self.shm_name, 0, info.shape, info.dtype)
            self.shm_camera.execute(info)
        
    def streaming(self, delay_time = 0.0):
        '''
        Start streaming.
        
        Parameters:
        - delay_time: float, optional, default: 0.0, the delay time before collecting data.
        '''
        if self.with_streaming is False:
            raise AttributeError('If you want to use streaming function, the "shm_name" attribute should be set correctly.')
        self.thread = threading.Thread(target = self.streaming_thread, kwargs = {'delay_time': delay_time})
        self.thread.setDaemon(True)
        self.thread.start()
    
    def streaming_thread(self, delay_time = 0.0):
        time.sleep(delay_time)
        self.is_streaming = True
        self.logger.info('Start streaming ...')
        while self.is_streaming:
            self.shm_camera.execute((self.get_info()).astype(np.uint8))
            time.sleep(1.0 / self.streaming_freq)
    
    def stop_streaming(self, permanent = True):
        '''
        Stop streaming process.

        Parameters:
        - permanent: bool, optional, default: True, whether the streaming process is stopped permanently.
        '''
        self.is_streaming = False
        self.thread.join()
        self.logger.info('Close streaming.')
        if permanent:
            self._close_shm()
            self.with_streaming = False
    
    def _close_shm(self):
        '''
        Close shared memory objects.
        '''
        if self.with_streaming:
            self.shm_camera.close()
        

    def get_info(self):
        '''
        Get the camera observation (RGB).
        '''
        return np.array([])
    
    def stop(self):
        '''
        Stop.
        '''
        if self.is_streaming:
            self.stop_streaming(permanent = True)
        else:
            self._close_shm()



class RGBDCameraBase(object):
    def __init__(
        self, 
        logger_name: str = "RGBD Camera",
        shm_name_rgb: str = None, 
        shm_name_depth: str = None,
        streaming_freq: int = 30, 
        **kwargs
    ): 
        '''
        Initialization.
        
        Parameters:
        - logger_name: str, optional, default: "RGBDCamera", the name of the logger;
        - shm_name_rgb: str, optional, default: None, the shared memory name of the camera RGB data, None means no shared memory object for RGB data;
        - shm_name_depth: str, optional, default: None, the shared memory name of the camera depth data, None means no shared memory object for depth data;
        - streaming_freq: int, optional, default: 30, the streaming frequency.
        '''
        super(RGBDCameraBase, self).__init__()
        logging.setLoggerClass(ColoredLogger)
        self.logger = logging.getLogger(logger_name)
        self.is_streaming = False
        self.with_streaming_rgb = (shm_name_rgb is not None)
        self.with_streaming_depth = (shm_name_depth is not None)
        self.with_streaming = self.with_streaming_rgb or self.with_streaming_depth
        self.streaming_freq = streaming_freq
        self.shm_name_rgb = shm_name_rgb
        self.shm_name_depth = shm_name_depth
        self._prepare_shm()

    def _prepare_shm(self):
        '''
        Prepare shared memory objects.
        '''
        if self.with_streaming:
            rgb, depth = self.get_info()
            rgb = np.array(rgb).astype(np.uint8)
            depth = np.array(depth).astype(np.float32)
            if self.with_streaming_rgb:
                self.shm_camera_rgb = SharedMemoryManager(self.shm_name_rgb, 0, rgb.shape, rgb.dtype)
                self.shm_camera_rgb.execute(rgb)
            if self.with_streaming_depth:
                self.shm_camera_depth = SharedMemoryManager(self.shm_name_depth, 0, depth.shape, depth.dtype)
                self.shm_camera_depth.execute(depth)
        
    def streaming(self, delay_time = 0.0):
        '''
        Start streaming.
        
        Parameters:
        - delay_time: float, optional, default: 0.0, the delay time before collecting data.
        '''
        if self.with_streaming is False:
            raise AttributeError('If you want to use streaming function, either "shm_name_rgb" attribute or "shm_name_depth" attribute should be set correctly.')
        self.thread = threading.Thread(target = self.streaming_thread, kwargs = {'delay_time': delay_time})
        self.thread.setDaemon(True)
        self.thread.start()
    
    def streaming_thread(self, delay_time = 0.0):
        time.sleep(delay_time)
        self.is_streaming = True
        self.logger.info('Start streaming ...')
        while self.is_streaming:
            rgb, depth = self.get_info()
            rgb = np.array(rgb).astype(np.uint8)
            depth = np.array(depth).astype(np.float32)
            if self.with_streaming_rgb:
                self.shm_camera_rgb.execute(rgb)
            if self.with_streaming_depth:
                self.shm_camera_depth.execute(depth)
            time.sleep(1.0 / self.streaming_freq)
    
    def stop_streaming(self, permanent = True):
        '''
        Stop streaming process.

        Parameters:
        - permanent: bool, optional, default: True, whether the streaming process is stopped permanently.
        '''
        self.is_streaming = False
        self.thread.join()
        self.logger.info('Close streaming.')
        if permanent:
            self._close_shm()
            self.with_streaming = False
    
    def _close_shm(self):
        '''
        Close shared memory objects.
        '''
        if self.with_streaming_rgb:
            self.shm_camera_rgb.close()
        if self.with_streaming_depth:
            self.shm_camera_depth.close()

    def get_info(self):
        '''
        Get the camera observation (RGB-D).
        '''
        return np.array([]), np.array([])

    def stop(self):
        '''
        Stop.
        '''
        if self.is_streaming:
            self.stop_streaming(permanent = True)
        else:
            self._close_shm()
