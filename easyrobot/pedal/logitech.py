'''
Logitech G29 API

Author: Hao-Shu Fang, Hongjie Fang
'''

import pygame
import logging
import numpy as np

from easyrobot.pedal.base import PedalBase


class LogitechG29Pedal(PedalBase):
    '''
    Logitech G29 pedal API.
    '''
    def __init__(
        self,
        shm_name: str = "none", 
        streaming_freq: int = 30, 
        **kwargs
    ):
        '''
        Initialization.
        
        Parameters:
        - shm_name: str, optional, default: "none", the shared memory name of the pedal data, "none" means no shared memory object;
        - streaming_freq: int, optional, default: 30, the streaming frequency.
        '''
        pygame.init()
        try:
            self.js = pygame.joystick.Joystick(0)
        except:
            raise RuntimeError('Could not find joystick of the Logitech G29 pedal.')
        self.js.init()
        self.num_axes = self.js.get_numaxes()
        self.num_buttons = self.js.get_numbuttons()
        logging.info('[Pedal] Activated.')
        super(LogitechG29Pedal, self).__init__(
            shm_name = shm_name,
            streaming_freq = streaming_freq,
            **kwargs
        )

    def get_axes(self):
        '''
        Get the axes of the pedal.

        Returns:
        - axes_value: the values of each axis.
            * index 0: wheel;
            * index 1: clutch;
            * index 2: gas;
            * index 3: break.
        '''
        pygame.event.get()
        axes_values = []
        for a in range(self.num_axes):
            axis = self.js.get_axis(a)
            axes_values.append(axis)
        return np.array(axes_values)

    def get_buttons(self):
        '''
        Get the button presses information of the pedal.

        Returns:
        - button_presses: the button presses information
            * index 4: right paddle;
            * index 5: left paddel.
        '''
        pygame.event.get()
        button_presses = []
        for b in range(self.num_buttons):
            button = self.js.get_button(b)
            button_presses.append(button)
        return np.array(button_presses)

    def get_info(self):
        return np.concatenate((self.get_axes(), self.get_buttons))
