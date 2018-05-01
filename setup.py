from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    author='William Scales',
    author_email='william@wscales.com',
    description='Code for toy self driving car project',
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    name='selfdrivingcar',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    python_requires='>=3.6',
    url='https://github.com/williamscales/selfdrivingcar',
    version='0.1',
)
