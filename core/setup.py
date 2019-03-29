from setuptools import setup, find_packages


setup(
    name='zeit.newsletter',
    version='1.5.6.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi Content-Type Newsletter",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'gocept.lxml',
        'gocept.httpserverlayer',
        'gocept.selenium >= 2.1.10.dev0',
        'grokcore.component',
        'mock',
        'pytz',
        'setuptools',
        'zeit.addcentral',
        'zeit.edit >= 2.17.0.dev0',
        'zeit.cms >= 3.8.0.dev0',
        'zeit.content.image',
        'zeit.content.video',
        'zeit.connector',
        'zeit.optivo',
        'zope.interface',
        'zope.cachedescriptors',
        'zope.component',
        'zope.container',
    ],
    entry_points={
        'fanstatic.libraries': [
            'zeit_newsletter=zeit.newsletter.browser.resources:lib',
        ],
    },
)
