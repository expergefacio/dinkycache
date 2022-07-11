from setuptools import setup

VERSION = '0.9'
DESCRIPTION = 'Sqlite based cache for python projects'

setup(
  name='dinkycache',
  version='1',
  description=DESCRIPTION,
  author='eXpergefacio & Lanjelin',
  author_email='any@expdvl.com',
  packages=['dinkycache'],
  url='https://github.com/expergefacio/dinkycache',
  keywords=['dinkycache'],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.1',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    ],
  install_requires=['lzstring==1.0.4'],
)