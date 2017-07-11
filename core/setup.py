from setuptools import setup, find_packages

setup(
    name='zeit.brightcove',
    version='2.10.2.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description='Brightcove HTTP interface',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'gocept.runner>0.5.3',
        'grokcore.component',
        'grokcore.view',
        'lxml',
        'pytz',
        'setuptools',
        'zeit.addcentral',
        'zeit.cms>=2.104.0.dev0',
        'zeit.content.video>=2.7.4.dev0',
        'zeit.solr>=2.2.0.dev0',
        'zope.cachedescriptors',
        'zope.component',
        'zope.interface',
        'zope.schema',
    ],
    extras_require=dict(test=[
        'zeit.content.author',
    ]),
    entry_points="""
    [console_scripts]
    update-brightcove-repository=zeit.brightcove.update:_update_from_brightcove
    brightcove-import-playlists=zeit.brightcove.update2:import_playlists
    """
)
