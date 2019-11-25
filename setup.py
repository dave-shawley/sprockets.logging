#!/usr/bin/env python
import setuptools

import sprockets_logging


install_requires = []
setup_requires = []
tests_require = ['nose>=1.3,<2', 'tornado>3,<5']

setuptools.setup(
    name='sprockets.logging',
    version=sprockets_logging.version,
    description='Making logs nicer since 2015!',
    long_description=open('README.rst').read(),
    url='https://github.com/sprockets/sprockets.logging.git',
    author='Dave Shawley',
    author_email='daves@aweber.com',
    license='BSD',
    extras_require={'tornado': ['tornado>3,<5']},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    test_suite='nose.collector',
    zip_safe=True)
