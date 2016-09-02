from setuptools import setup, find_packages


setup(
    name='zeit.content.video',
    version='2.6.0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi Content-Type Video, Playlist",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit', 'zeit.content'],
    install_requires=[
        'gocept.form',
        'gocept.selenium',
        'grokcore.component',
        'lxml',
        'plone.testing',
        'pytz',
        'setuptools',
        'zeit.cms>=2.85.1.dev0',
        'zeit.connector',
        'zeit.solr>=2.2.0.dev0',
        'zope.annotation',
        'zope.app.zcmlfiles',
        'zope.component',
        'zope.dublincore',
        'zope.formlib',
        'zope.interface',
        'zope.schema',
        'zope.traversing',
    ],
    extras_require=dict(test=[
        'zeit.content.author',
    ]),
)
