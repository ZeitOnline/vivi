from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
NEWS = open(os.path.join(here, 'CHANGES.txt')).read()


version = '0.1dev'

install_requires = [
    'setuptools',
    'gocept.jslint>=0.2',
    'gocept.lxml',
    'grokcore.component',
    'lxml',
    'zc.resourcelibrary',
    'zeit.cms',
    'zeit.find',
    'zope.schema',
    'zope.interface',
]


setup(name='zeit.edit',
    version=version,
    description="Vivi Editor",
    long_description=README + '\n\n' + NEWS,
    # Get classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    # classifiers=[c.strip() for c in """
    #     Development Status :: 4 - Beta
    #     License :: OSI Approved :: MIT License
    #     Operating System :: OS Independent
    #     Programming Language :: Python :: 2.6
    #     Programming Language :: Python :: 2.7
    #     Programming Language :: Python :: 3
    #     Topic :: Software Development :: Libraries :: Python Modules
    #     """.split('\n') if c.strip()],
    # ],
    keywords='',
    author='',
    author_email='',
    url='',
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['zeit'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
)
