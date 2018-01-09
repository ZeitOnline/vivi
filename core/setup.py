from setuptools import setup, find_packages


setup(
    name='zeit.wysiwyg',
    version='3.0.2.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi legacy WYSIWYG editor",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'gocept.fckeditor[fanstatic]>=2.6.4.1-2',
        'lxml',
        'pytz',
        'rwproperty',
        'setuptools',
        'zc.iso8601',
        'zc.resourcelibrary',
        'zeit.cms>=3.2.0.dev0',
        'zeit.content.image>=2.13.6.dev0',
        'zope.app.pagetemplate',
        'zope.app.testing',
        'zope.cachedescriptors',
        'zope.component',
        'zope.formlib',
        'zope.interface',
        'zope.security',
        'zope.testing',
        'zope.traversing',
    ],
    extras_require=dict(test=[
        'zeit.content.gallery',
        'zeit.content.infobox',
        'zeit.content.portraitbox',
    ]),
    entry_points={
        'fanstatic.libraries': [
            'zeit_wysiwyg=zeit.wysiwyg.browser.resources:lib',
        ],
    },
)
