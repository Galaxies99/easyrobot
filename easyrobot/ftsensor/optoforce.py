'''
OptoForce F/T Sensor

Author: Hongjie Fang
'''

from easyrobot.ftsensor.ethernet import EthernetFTSensor


class OptoForceFTSensor(EthernetFTSensor):
    '''
    OptoForce Force/Torque Sensor.
    '''
    def __init__(
        self, 
        ip = '192.168.1.1',
        port = 49152,
        logger_name: str = "OptoForce F/T Sensor",
        shm_name: str = "none", 
        streaming_freq: int = 30, 
        **kwargs
    ):
        '''
        Initialization.

        Parameters:
        - ip: optional, default: '192.168.1.1', the IP address of the ethernet force/torque sensor;
        - port: optional, default: 49152, the port of the ethernet force/torque sensor;
        - logger_name: str, optional, default: "OptoForce F/T Sensor", the name of the logger;
        - shm_name: str, optional, default: "none", the shared memory name of the force/torque sensor data, "none" means no shared memory object;
        - streaming_freq: int, optional, default: 30, the streaming frequency.
        '''
        super(OptoForceFTSensor, self).__init__(
            ip = ip,
            port = port,
            scale = (10000, 100000),
            logger_name = logger_name,
            shm_name = shm_name,
            streaming_freq = streaming_freq
        )
    