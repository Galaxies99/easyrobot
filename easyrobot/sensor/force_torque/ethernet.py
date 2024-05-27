'''
Ethernet Force Torque Sensor Module

Author: Hongjie Fang

Ref: 
  [1] <Ethernet Axia F/T Sensor Manual>, available at https://www.ati-ia.com/zh-cn/app_content/documents/9610-05-Ethernet%20Axia.pdf
  [2] <OptoForce Installation and Operation Manual For Ethernet Converter>, available at https://manualzz.com/doc/26839390/ethernet---optoforce.
  [3] NetFT, Cameron Devine, Github, availabale at https://github.com/CameronDevine/NetFT
'''

import socket
import struct
import numpy as np

from easyrobot.sensor.force_torque.base import FTSensorBase


class EthernetFTSensor(FTSensorBase):
    '''
    Ethernet Force/Torque Sensor.
    '''
    def __init__(
        self, 
        ip = '192.168.1.1',
        port = 49152,
        scale = (1000, 1000),
        logger_name: str = "Ethernet F/T Sensor",
        shm_name: str = None, 
        streaming_freq: int = 30, 
        **kwargs
    ):
        '''
        Initialization.

        Parameters:
        - ip: optional, default: '192.168.1.1', the IP address of the ethernet force/torque sensor;
        - port: optional, default: 49152, the port of the ethernet force/torque sensor;
        - scale: tuple of (int, int), default: (1000, 1000), the scaling coefficient of the force and torque values;
        - logger_name: str, optional, default: "F/T Sensor", the name of the logger;
        - shm_name: str, optional, default: None, the shared memory name of the force/torque sensor data, None means no shared memory object;
        - streaming_freq: int, optional, default: 30, the streaming frequency.
        '''
        self.ip = ip
        self.port = port
        self.scale = np.array([scale[0]] * 3 + [scale[1]] * 3).astype(np.float32)
        self.mean = np.zeros((6, )).astype(np.float32)
        self.shm_name = shm_name
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect((self.ip, self.port))
        self.logger.info("Connected.")
        super(EthernetFTSensor, self).__init__(
            logger_name = logger_name,
            shm_name = shm_name,
            streaming_freq = streaming_freq,
            **kwargs
        )
    
    def send(self, command, data):
        '''
        Send a given command to the sensor.
        
        Parameters:
        - command: uint16, required, refer to the value according to the command table;
        - data: uint32, required, data according to the actual command.
        '''
        header = 0x1234
        msg = struct.pack('!HHI', header, command, data)
        self.socket.send(msg)
    
    def receive(self):
        '''
        Receive and unpack the response from the sensor.
        
        Returns:
        - np.array of float: The force and torque values received. The first three values are the forces recorded, and the last three are the measured torques.
        '''
        msg = self.socket.recv(1024)
        data = np.array(struct.unpack('!IIIiiiiii', msg)[3:]).astype(np.float32)
        self.data = data / self.scale - self.mean
        return self.data
    
    def measure(self, n):
        '''
        Request a given number of measurements from the sensor. Notice that this function requests a given number of samples from the sensor. These measurements must be received manually using the `receive` function.
        
        Parameters:
        - n: uint32, required, sample count.
        '''
        self.send(0x0002, n)
    
    def get_info(self):
        '''
        Get a single measurement from the sensor and return it. If the sensor is currently streaming, started by running `startStreaming`, then this function will simply return the most recently returned value.
        
        Returns:
        - np.array of float: The force and torque values received. The first three values are the forces recorded, and the last three are the measured torques.
        '''
        self.measure(n = 1)
        return self.receive()

    def get_force(self):
        '''
        Get a single force measurement from the sensor. Request a single measurement from the sensor and return it.
		
        Returns:
		- np.array of float: The force values received.
		'''
        return self.get_info()[:3]
    
    def get_torque(self):
        '''
        Get a single torque measurement from the sensor. Request a single measurement from the sensor and return it.
		
        Returns:
		- np.array of float: The torque values received.
        '''
        return self.get_info()[3:]
    
    def fetch_info(self):
        '''
        Fetch the most recent force/torque measurement.
        
        Returns:
        - np.array of float: The force and torque values received. The first three values are the forces recorded, and the last three are the measured torques.
        '''
        return self.data
    
    def fetch_force(self):
        '''
        Fetch the most recent force measurement.
		
        Returns:
		- np.array of float: The force values received.
        '''
        return self.fetch_info()[:3]
    
    def fetch_torque(self):
        '''
        Fetch the most recent torque measurement.
		
        Returns:
		- np.array of float: The torque values received.
        '''
        return self.fetch_info()[3:]
    
    def zero(self):
        '''
        Remove the mean found with `tare` to start receiving raw sensor values.
        '''
        self.mean = np.zeros((6, )).astype(np.float32)
    
    def tare(self, n = 100):
        '''
        Tare the sensor. This function takes a given number of readings from the sensor and averages them. This mean is then stored and subtracted from all future measurements.
		
        Parameters:
		- n: int, optional, default: 100, the number of samples to use in the mean.
		
        Returns:
        - np.array of float: The mean values calculated.
        '''
        self.zero()
        mean = np.zeros((6, )).astype(np.float32)
        self.measure(n = n)
        for _ in range(n):
            mean += self.receive()
        self.mean = mean / float(n)
        return self.mean
