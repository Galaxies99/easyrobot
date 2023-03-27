'''
ATI F/T Sensor.

Author: Hongjie Fang
'''

from easyrobot.ftsensor.ethernet import EthernetFTSensor


class ATIFTSensor(EthernetFTSensor):
    '''
    ATI Force/Torque Sensor.
    '''
    def __init__(
        self, 
        ip = '192.168.1.1',
        port = 49152,
        shm_name: str = "none", 
        streaming_freq: int = 30, 
        **kwargs
    ):
        '''
        Initialization.

        Parameters:
        - ip: optional, default: '192.168.1.1', the IP address of the ethernet force/torque sensor;
        - port: optional, default: 49152, the port of the ethernet force/torque sensor;
        - shm_name: str, optional, default: "none", the shared memory name of the force/torque sensor data, "none" means no shared memory object;
        - streaming_freq: int, optional, default: 30, the streaming frequency.
        '''
        super(ATIFTSensor, self).__init__(
            ip = ip,
            port = port,
            scale = (1000000, 1000000),
            shm_name = shm_name,
            streaming_freq = streaming_freq,
            **kwargs
        )
    