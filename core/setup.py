from setuptools import setup, find_packages


setup(
    name='zeit.connector',
    version='2.7.2',
    author='Tomas Zerolo, gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="DAV interface",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'ZConfig',
        'ZODB',
        'gocept.cache>=0.2.2',
        'gocept.lxml',
        'gocept.runner>=0.2',
        'mock',
        'persistent',
        'setuptools',
        'transaction',
        'zc.queue',
        'zc.set',
        'zope.annotation',
        'zope.app.appsetup',
        'zope.app.component>=3.4b3',
        'zope.app.file',
        'zope.app.testing',
        'zope.app.zcmlfiles',
        'zope.authentication',
        'zope.cachedescriptors',
        'zope.component',
        'zope.file',
        'zope.interface',
        'zope.location>=3.4b2',
        'zope.testing',
    ],
    entry_points="""
        [console_scripts]
        refresh-cache=zeit.connector.invalidator:invalidate_whole_cache
        """
)
