#!/usr/bin/env python

from setuptools import setup, find_packages
from os.path import join, dirname
import attachments

def desc():
    return open(join(dirname(__file__), 'README.rst')).read() \
            + '\n' \
            + open(join(dirname(__file__), 'ChangeLog.rst')).read()

setup(
    name='django-extended-attachments',
    description='A generic Django application to attach Files (Attachments) to any model',
    long_description=desc(),
    license='BSD',
    version=attachments.__version__,
    author=attachments.__author__,
    author_email=attachments.__email__,
    url='http://vehq.ru/project/django-extended-attachments/',
    download_url='http://hg.vehq.ru/django-extended-attachments/archive/%s.tar.bz2' % attachments.__version__,
    keywords=['Django', 'attachments', 'antivirus'],
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    package_data={
        'attachments': [
            'templates/attachments/*.html',
            'locale/*/*/*',
        ]
    },
    install_requires=['django_extensions', 'django>=1.2'], # python >= 2.6
    platforms='any',
    zip_safe=False,
)
