from setuptools import setup, find_packages
import os


with open('README.md') as f:
    long_description = f.read()

setup(
    name='py86',
    version='0.1',
    packages=find_packages(),
    entry_points={'console_scripts': ['py86=py86.py86:asm']},
    test_suite='test.testasm',

    # dependencies
    install_requires=['sly==0.3'],  # all parsing
    python_requires='>=3.7.0',      # dataclasses

    # metadata
    author='Loan Tricot',
    author_email='ltricot@gmail.com',
    description='A python assembler for Y86',
    long_description=long_description,
    long_description_content_type='text/markdown',
    project_urls = {'Source Code': 'https://github.com/ltricot/py86'},

    classifiers=[
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux'
    ]
)


# make sure shim is created
if os.path.exists('~/.pyenv'):
    os.system('pyenv rehash && hash -r')

