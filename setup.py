import setuptools

setuptools.setup(
    name='closedloop_control',
    version='0.0.1',
    author='Mengzhan Liufu & Sameera Shridhar',
    author_email='mliufu@uchicago.edu',
    description='Trodes-based closed loop control system',
    url='https://github.com/JohnLauFoo/ClosedLoopControl_Yu',
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'ipython',
        'nbformat',
        'trodesnetwork==0.0.9'
    ],
)