from setuptools import setup, find_packages

setup(
    name = 'easyrobot',
    version = '0.0.3',
    license = 'MIT',
    description = 'An easy and unified interface for robot (and grippers, etc.)',
    author = "Hongjie Fang",
    author_email = "tony.fang.galaxies@gmail.com, galaxies@sjtu.edu.cn",
    maintainer = "Hongjie Fang",
    maintainer_email = "tony.fang.galaxies@gmail.com, galaxies@sjtu.edu.cn",
    packages = find_packages(exclude = ['docs', 'assets']),
    include_package_data = True,
    install_requires = [
        'numpy',
        'pyserial',
        'pygame',
        'modbus_tk'
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    zip_safe = False
)