from setuptools import setup


setup(
  name='dinkycache',
  version='1',
  description='sqlite based cache for python projects',
  author='eXpergefacio & Lanjelin',
  author_email='any@expdvl.com',
  packages=['dinkycache'],
  package_data={},
  url='https://github.com/expergefacio/dinkycache',
  keywords=['dinkycache'],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.1',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    ],
    install_requires=['lzstring==1.0.4'],
)