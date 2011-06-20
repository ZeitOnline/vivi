# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

from setuptools import setup, find_packages

setup(
    name='zeit.content.rawxml',
    version='0.4.1dev',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://svn.gocept.com/repos/gocept-int/zeit.cms/zeit.content.rawxml',
    description="""\
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages = ['zeit', 'zeit.content'],
    install_requires=[
        'setuptools',
        'zeit.cms>1.4',
        'z3c.etestbrowser',
    ])
