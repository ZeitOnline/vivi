# Copyright (c) 2009-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from setuptools import setup, find_packages


setup(
    name='zeit.content.cp',
    version='2.0.1.dev0',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://intra.gocept.com/projects/projects/zeit-cms',
    description="""\
""",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages=['zeit', 'zeit.content'],
    install_requires=[
        'feedparser',
        'gocept.cache',
        'gocept.jslint>=0.2',
        'gocept.lxml',
        'gocept.mochikit>=1.4.2.2',
        'gocept.runner>-0.4',
        'gocept.selenium>=0.6',
        'grokcore.component',
        'lxml',
        'setuptools',
        'stabledict',
        'unittest2',
        'zc.sourcefactory',
        'zeit.content.video',
        'zeit.cms>=2.2.0.dev0',
        'zeit.content.quiz>=0.4.2',
        'zeit.edit',
        'zeit.find >= 0.4',
        'zeit.solr',
        'zope.app.appsetup',
        'zope.app.generations',
        'zope.app.pagetemplate',
        'zope.component',
        'zope.container>=3.8.1',
        'zope.event',
        'zope.formlib',
        'zope.i18n',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.viewlet',
    ],
    entry_points="""
        [console_scripts]
        refresh-feeds = zeit.content.cp.feed:refresh_all
        sweep-teasergroup-repository = zeit.content.cp.teasergroup.teasergroup:sweep_repository
    """,
)
