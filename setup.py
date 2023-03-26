from setuptools import setup, find_packages

setup(
    name = 'easyrobot',
    version = '0.0.1',
    description = 'An easy and unified interface for robot (and grippers, etc.)',
    author = "Hongjie Fang",
    author_email = "tony.fang.galaxies@gmail.com, galaxies@sjtu.edu.cn",
    maintainer = "Hongjie Fang",
    maintainer_email = "tony.fang.galaxies@gmail.com, galaxies@sjtu.edu.cn",
    package = find_packages(include = [
        'easyrobot', 
    #   'easyrobot.robot',
        'easyrobot.gripper', 
        'easyrobot.pedal',
        'easyrobot.utils',
    #   'easyrobot.robot.*',
        'easyrobot.gripper.*',
        'easyrobot.pedal.*',
        'easyrobot.utils.*'
    ]),
    install_requires = [
        'numpy',
        'pyserial',
        'pygame',
        'modbus_tk'
    ]
)