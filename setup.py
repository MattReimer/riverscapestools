# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""
"""
A Lot of this methodology was "borrowed" from
    - https://github.com/jgehrcke/python-cmdline-bootstrap/blob/master/bootstrap/bootstrap.py
"""

import re
from setuptools import setup

install_requires = [
    'argparse'
]

version = re.search(
      '^__version__\s*=\s*"(.*)"',
      open('rspupload/rspupload.py').read(),
      re.M
).group(1)

with open("README.md", "rb") as f:
      long_descr = f.read().decode("utf-8")

setup(
      name='rspupload',
      description='A Riverscapes Uploader tool',
      url='https://github.com/Riverscapes/rspupload',
      author='Matt Reimer',
      author_email='matt@northarrowresearch.com',
      license='MIT',
      packages=['rspupload'],
      zip_safe=False,
      install_requires=install_requires,
      entry_points={
            "console_scripts": ['rspupload = rspupload:main']
      },
      version=version,
      long_description=long_descr,
)