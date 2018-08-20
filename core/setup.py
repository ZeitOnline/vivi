from setuptools import setup, find_packages


setup(
    name='zeit.content.link',
    version='2.2.4.dev0',
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
        'zeit.cms>=2.90.0.dev0',
        'zeit.content.image',
        'zeit.connector',
        'zeit.push>=1.21.0.dev0',
        'zope.cachedescriptors',
        'zope.component',
        'zope.formlib',
        'zope.interface',
        'zope.publisher',
        'zope.schema',
        'zope.testbrowser',
    ],
    entry_points={
        'fanstatic.libraries': [
            'zeit_content_link=zeit.content.link.browser.resources:lib',
        ]}
)
