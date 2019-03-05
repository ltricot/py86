from setuptools import setup, find_packages

setup(
    name='py86',
    version='0.1',
    packages=find_packages(),

    # dependencies
    install_requires=['sly==0.3'],  # all parsing
    python_requires='>=3.7.0',      # dataclasses

    # metadata
    author='Loan Tricot',
    author_email='ltricot@gmail.com',
)

