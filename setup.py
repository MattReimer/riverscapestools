# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""
"""
A Lot of this methodology was "borrowed" from
    - https://github.com/jgehrcke/python-cmdline-bootstrap/blob/master/bootstrap/bootstrap.py
"""

import re
from setuptools import setup

install_requires = [
    'argparse', 'boto3', 'botocore'
]

version = re.search(
      '^__version__\s*=\s*"(.*)"',
      open('riverscapestools/__version__.py').read(),
      re.M
).group(1)

with open("README.md", "rb") as f:
      long_descr = f.read().decode("utf-8")

setup(
      name='riverscapestools',
      description='A Riverscapes Uploader tool',
      url='https://github.com/Riverscapes/rspupload',
      author='Matt Reimer',
      author_email='matt@northarrowresearch.com',
      license='MIT',
      packages=['.', 'riverscapestools.s3', 'riverscapestools.program', 'riverscapestools.logger'],
      zip_safe=False,
      install_requires=install_requires,
      entry_points={
            "console_scripts": ['rspupload = riverscapestools.rspupload:main',
                                'rsplist = riverscapestools.rsplist:main',
                                'rspdownload = riverscapestools.rspdownload:main']
      },
      version=version,
      long_description=long_descr,
)