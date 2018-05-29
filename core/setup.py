from setuptools import setup, find_packages


setup(
    name='zeit.find',
    version='2.7.3',
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
        'zeit.solr>=2.8.0.dev0',
    ],
    entry_points={
        'fanstatic.libraries': [
            'zeit_find=zeit.find.browser.resources:lib',
        ],
    },
)
