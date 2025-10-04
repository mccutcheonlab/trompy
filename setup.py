# -*- coding: utf-8 -*-
"""
setup file for trompy pypi package
"""
from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

from distutils.core import setup

# read version from trompy/_version.py without importing the package
def read_version():
  here = path.abspath(path.dirname(__file__))
  ver_file = path.join(here, 'trompy', '_version.py')
  namespace = {}
  with open(ver_file, 'r', encoding='utf-8') as vf:
    exec(vf.read(), namespace)
  return namespace.get('__version__', '0.0.0')

setup(
  name = 'trompy',         # How you named your package folder (MyLib)
  packages = ['trompy'],   # Chose the same as "name"
  version = read_version(),      # read single-source version
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'A collection of tools for data analysis and plotting that originated in the McCutcheon Lab (UiT, Tromso)',   # Give a short description about your library
  long_description = long_description,
  long_description_content_type = 'text/markdown',
  author = 'James E McCutcheon',                   # Type in your name
  author_email = 'j.mccutcheon@uit.no',      # Type in your E-Mail
  url = 'https://github.com/mccutcheonlab',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/mccutcheonlab/trompy/archive/v0.15.8.tar.gz',    # I explain this later on
  keywords = ['neuroscience', 'behavior'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'numpy',
          'matplotlib',
          'xlrd',
          'scipy',
          'pandas',
          'xlsxwriter',
          'tdt',
          'openpyxl',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)