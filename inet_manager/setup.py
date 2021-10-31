from setuptools import setup

setup(
    name='inet_manager',
    version='1.0.0',
    author='Skyler Arnold',
    packages=['inet_manager'],
    entry_points={'console_scripts': ['inet-cli=inet_manager.cli.__main__:main']},
    zip_safe=False
)