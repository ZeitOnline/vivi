from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
NEWS = open(os.path.join(here, 'CHANGES.txt')).read()

setup(
    name='zeit.edit',
    version='2.1.8.dev0',
    description="Vivi Editor",
    long_description=README + '\n\n' + NEWS,
    keywords='',
    author='',
    author_email='',
    url='',
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['zeit'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'gocept.jslint>=0.2',
        'gocept.lxml',
        'gocept.selenium',
        'grokcore.component',
        'lxml',
        'mock',
        'zc.resourcelibrary',
        'zeit.cms>=2..13.0dev',
        'zeit.find>=2.2.dev.0',
        'zope.schema',
        'zope.interface',
    ],
)
