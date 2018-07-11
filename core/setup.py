from setuptools import setup, find_packages


setup(
    name='zeit.find',
    version='3.0.0.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi UI for querying solr",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'gocept.httpserverlayer',
        'gocept.selenium',
        'grokcore.component',
        'plone.testing',
        'setuptools',
        'zc.iso8601',
        'zeit.cms >= 3.12.0.dev0',
        'zeit.content.image',
    ],
    entry_points={
        'fanstatic.libraries': [
            'zeit_find=zeit.find.browser.resources:lib',
        ],
        'console_scripts': [
            'search-elastic=zeit.find.cli:search_elastic',
        ],
    },
)
