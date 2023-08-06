'''
Dahuan Gripper Interface

Author: Junfeng Ding, Hongjie Fang
'''

import time
import serial
import numpy as np
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu

from easyrobot.gripper.base import GripperBase


class DahuanAG95Gripper(GripperBase):
    '''
    Dahuan AG95 Gripper API.
    '''
    def __init__(
        self, 
        port: str,
        logger_name: str = "Dahuan Gripper",
        shm_name: str = None, 
        streaming_freq: int = 30, 
        **kwargs
    ):
        '''
        Initialization.
        
        Parameters
        ----------
        - port: str, required, the port of the Dahuan AG95 Gripper;
        - logger_name: str, optional, default: "Dahuan Gripper", the name of the logger;
        - shm_name: str, optional, default: None, the shared memory name of the gripper data, None means no shared memory object;
        - streaming_freq: int, optional, default: 30, the streaming frequency.
        '''
        self.master = modbus_rtu.RtuMaster(
            serial.Serial(
                port = port, baudrate = 115200, bytesize = 8, parity = "N", stopbits = 1
            )
        )
        self.master.open()
        if not self.master._is_opened:
            raise RuntimeError('Needs permission in port {} to control the Dahuan AG95 gripper.'.format(port))
        self.master.set_timeout(2.0)
        self.master.set_verbose(True)
        self.last_position = 1000
        self.last_force = 100
        self.last_timestamp = int(time.time() * 1000)
        self.activate()
        self.set_force(100)
        super(DahuanAG95Gripper, self).__init__(
            logger_name = logger_name,
            shm_name = shm_name,
            streaming_freq = streaming_freq,
            **kwargs
        )
        self.logger.info('Activated.')

    def activate(self):
        '''
        Initialization the gripper.
        '''
        self.master.execute(1, cst.WRITE_SINGLE_REGISTER, 0x0100, 2, 0x00A5)
        return_data = self.master.execute(1, cst.READ_HOLDING_REGISTERS, 0x0200, 1)
        while return_data != 1:
            return_data = self.master.execute(1, cst.READ_HOLDING_REGISTERS, 0x0200, 1)[0]
            time.sleep(0.1)
    
    def action(self, position, force = 100, **kwargs):
        '''
        Send the control command to the gripper.

        Parameters:
        - position: int, required, between 0 and 1000, the width permillage; the corresponding real-world width range is 0mm ~ 95mm;
        - force: int, required, between 20 and 100, the force percent; the corresponding real-world force range is 45N ~ 160N.
        '''
        position = np.clip(position, 0, 1000)
        force = np.clip(force, 20, 100)
        return_data = self.master.execute(1, cst.WRITE_SINGLE_REGISTER, 0x0101, 2, force)[1]
        assert return_data == force
        return_data = self.master.execute(1, cst.WRITE_SINGLE_REGISTER, 0x0103, 2, position)[1]
        assert return_data == position
        self.last_position = position
        self.last_force = force
        self.last_timestamp = int(time.time() * 1000)

    def open_gripper(self):
        '''
        Open the gripper.
        '''
        self.set_width(1000)

    def close_gripper(self):
        '''
        Close the gripper.
        '''
        self.set_width(0)

    def get_info(self):
        '''
        Get the current gripper information, including width, current, status and last command.

        Returns:
        - width: the width of the gripper, from 0 to 1000;
        - current: the current value of the gripper;
        - status:
          * 0 : moving;
          * 1 : stop and reach target position;
          * 2 : stop and catch object;
          * 3 : cathed object and then object is fallen;
        - width, force, timestamp of the last command.
        '''
        width = self.master.execute(1, cst.READ_HOLDING_REGISTERS, 0x0202, 1)[0]
        current = self.master.execute(1, cst.READ_HOLDING_REGISTERS, 0x0204, 1)[0]
        status = self.master.execute(1, cst.READ_HOLDING_REGISTERS, 0x0201, 1)[0]
        return np.array([width[0], current[0], status[0], self.last_position, self.last_force, self.last_timestamp]).astype(np.int64)
