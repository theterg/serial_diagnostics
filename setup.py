from setuptools import setup, find_packages

setup(
    name='serial_diagnostics',
    version='0.1',
    description='Logging and analysis tools for working with serial ports',
    packages=find_packages(exclude=['build', 'dist', '*.egg-info']),
    install_requires=['pyserial', 'colorama'],
    entry_points = {
        'console_scripts':
            ['seriallogger=serial_diagnostics.seriallogger:main'],
    },
)
