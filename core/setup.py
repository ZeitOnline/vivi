from setuptools import setup, find_packages


setup(
    name='zeit.content.link',
    version='2.1.1.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de',
    description="vivi Content-Type Link",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit', 'zeit.content'],
    install_requires=[
        'grokcore.component',
        'lxml',
        'setuptools',
        'zc.sourcefactory',
        'zeit.cms>=2.31.0.dev0',
        'zeit.content.image',
        'zeit.connector',
        'zeit.push>=1.7.0.dev0',
        'zope.cachedescriptors',
        'zope.component',
        'zope.formlib',
        'zope.interface',
        'zope.publisher',
        'zope.schema',
        'zope.testbrowser',
    ],
)
