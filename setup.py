# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='django-tenants',
    version='2.0.0',
    author=u'Kiss György',
    author_email='kissgyorgy@me.com',
    packages=find_packages(),
    url='https://github.com/stakingadmin/django-tenants',
    license='MIT',
    description='Multitenancy support for Django with PostgreSQL schemas.',
    long_description=open('README.rst').read(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'Django>=1.6,<1.7',
        'psycopg2',
        'django-debug-toolbar'
    ],
)
