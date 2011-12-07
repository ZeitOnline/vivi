# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from setuptools import setup, find_packages


setup(
    name='zeit.content.video',
    version='2.0.5dev',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://svn.gocept.com/repos/gocept-int/zeit.content.video',
    description="""\
""",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages=['zeit', 'zeit.content'],
    install_requires=[
        'gocept.form',
        'gocept.selenium',
        'grokcore.component',
        'lxml',
        'pytz',
        'setuptools',
        'zeit.cms>=1.51.1dev',
        'zeit.connector',
        'zeit.solr',
        'zope.annotation',
        'zope.app.zcmlfiles',
        'zope.component',
        'zope.dublincore',
        'zope.formlib',
        'zope.interface',
        'zope.schema',
        'zope.traversing',
    ],
)
