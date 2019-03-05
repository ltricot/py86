from setuptools import setup, find_packages
import os


setup(
    name='py86',
    version='0.1',
    packages=find_packages(),
    entry_points={'console_scripts': ['py86=py86.py86:asm']},

    # dependencies
    install_requires=['sly==0.3'],  # all parsing
    python_requires='>=3.7.0',      # dataclasses

    # metadata
    author='Loan Tricot',
    author_email='ltricot@gmail.com',
)


# make sure shim is created
if os.path.exists('~/.pyenv'):
    os.system('pyenv rehash && hash -r')

