from setuptools import setup, find_packages

setup(
    name='zeit.brightcove',
    version='2.12.2.dev0',
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
        'zeit.cms >= 3.0.dev0',
        'zeit.content.video>=3.0.0.dev0',
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
    brightcove-import-playlists=zeit.brightcove.update:import_playlists
    """
)
