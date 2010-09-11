#!/usr/bin/env python

import sys
import os
from setuptools import setup, find_packages



_top_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_top_dir, "lib"))
try:
    import sources
finally:
    del sys.path[0]
README = open(os.path.join(_top_dir, 'README.md')).read()

setup(name='sources',
    version=sources.__version__,
    description="a command-line script for getting/updating source dirs from a config file giving SCC URLs",
    classifiers=[c.strip() for c in """
        Development Status :: 5 - Production/Stable
        Environment :: Console
        Intended Audience :: Developers
        License :: OSI Approved :: MIT License
        Operating System :: OS Independent
        Programming Language :: Python :: 2
        Programming Language :: Python :: 2.5
        Programming Language :: Python :: 2.6
        Programming Language :: Python :: 2.7
        Programming Language :: Python :: 3
        Programming Language :: Python :: 3.1
        Topic :: Software Development :: Libraries :: Python Modules
        """.split('\n') if c.strip()],
    keywords='sources scc git hg subversion svn',
    author='Trent Mick',
    author_email='trentm@gmail.com',
    maintainer='Trent Mick',
    maintainer_email='trentm@gmail.com',
    url='http://github.com/trentm/sources',
    license='MIT',
    py_modules=["sources"],
    package_dir={"": "lib"},
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts':
            ['sources=sources:main']
    }
)

