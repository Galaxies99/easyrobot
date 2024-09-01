'''
Pedal Base Interface.

Author: Hongjie Fang.
'''

import time
import logging
import threading
import numpy as np

from easyrobot.utils.logger import ColoredLogger
from easyrobot.utils.shared_memory import SharedMemoryManager


class PedalBase(object):
    def __init__(
        self, 
        logger_name: str = "Pedal",
        shm_name: str = None, 
        streaming_freq: int = 30, 
        **kwargs
    ):
        '''
        Initialization.
        
        Parameters:
        - logger_name: str, optional, default: "Pedal", the name of the logger;
        - shm_name: str, optional, default: None, the shared memory name of the pedal data, None means no shared memory object;
        - streaming_freq: int, optional, default: 30, the streaming frequency.
        '''
        super(PedalBase, self).__init__()
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
            info = np.array(self.get_info()).astype(np.float32)
            self.shm_pedal = SharedMemoryManager(self.shm_name, 0, info.shape, info.dtype)
            self.shm_pedal.execute(info)

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
            self.shm_pedal.execute(np.array(self.get_info()).astype(np.float32))
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
            self.shm_pedal.close()
    
    def get_info(self):
        '''
        Get the pedal information.
        '''
        return np.array([])
    
    def action(self, *args, **kwargs):
        '''
        Unified pedal action.
        '''
        pass

    def stop(self):
        '''
        Stop.
        '''
        if self.is_streaming:
            self.stop_streaming(permanent = True)
        else:
            self._close_shm()