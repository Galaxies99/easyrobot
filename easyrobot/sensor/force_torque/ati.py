'''
ATI F/T Sensor.

Author: Hongjie Fang
'''

from easyrobot.sensor.force_torque.ethernet import EthernetFTSensor


class ATIFTSensor(EthernetFTSensor):
    '''
    ATI Force/Torque Sensor.
    '''
    def __init__(
        self, 
        ip = '192.168.1.1',
        port = 49152,
        logger_name: str = "ATI F/T Sensor",
        shm_name: str = None, 
        streaming_freq: int = 30, 
        **kwargs
    ):
        '''
        Initialization.

        Parameters:
        - ip: optional, default: '192.168.1.1', the IP address of the ethernet force/torque sensor;
        - port: optional, default: 49152, the port of the ethernet force/torque sensor;
        - logger_name: str, optional, default: "ATI F/T Sensor", the name of the logger;
        - shm_name: str, optional, default: None, the shared memory name of the force/torque sensor data, None means no shared memory object;
        - streaming_freq: int, optional, default: 30, the streaming frequency.
        '''
        super(ATIFTSensor, self).__init__(
            ip = ip,
            port = port,
            scale = (1000000, 1000000),
            logger_name = logger_name,
            shm_name = shm_name,
            streaming_freq = streaming_freq,
            **kwargs
        )
    