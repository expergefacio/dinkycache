from setuptools import setup
import io

"""
python -m pip install twine
python setup.py sdist bdist_wheel
twine upload --skip-existing dist/*
"""

VERSION = '1.0.3'
DESCRIPTION = 'Sqlite based cache for python projects'
LONG_DESCRIPTION = io.open('README.md', encoding='utf8').read()

setup(
  name='dinkycache',
  version=VERSION,
  description=DESCRIPTION,
  long_description=LONG_DESCRIPTION,
  long_description_content_type='text/markdown',
  author='eXpergefacio & Lanjelin',
  author_email='dinky@dominic.no',
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