from setuptools import setup, find_packages


setup(
    name='zeit.addcentral',
    version='1.1.7.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='https://www.zeit.de/',
    description="vivi add content portlet",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'gocept.selenium',
        'setuptools',
        'zeit.cms>=2.90.0.dev0',
        'zeit.content.image',
        'zope.app.pagetemplate',
        'zope.browser',
        'zope.cachedescriptors',
        'zope.formlib',
        'zope.interface',
        'zope.publisher',
        'zope.schema',
        'zope.session',
        'zope.viewlet',
    ],
    extras_require=dict(test=[
        'zeit.content.image>=2.13.6.dev0',
    ]),
    entry_points={
        'fanstatic.libraries': [
            'zeit_addcentral=zeit.addcentral.resources:lib',
        ],
    },
)
