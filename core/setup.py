from setuptools import setup, find_packages

setup(
    name='zeit.find',
    version='2.3.1.dev0',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://svn.gocept.com/repos/gocept-int/zeit.find',
    description="""\
""",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages=['zeit'],
    install_requires=[
        'gocept.httpserverlayer',
        'gocept.selenium',
        'grokcore.component',
        'plone.testing',
        'setuptools',
        'zc.iso8601',
        'zeit.cms>=2.20.0.dev0',
        'zeit.content.image',
        'zeit.solr>=2.0',
    ],
    entry_points={
        'fanstatic.libraries': [
            'zeit_find=zeit.find.browser.resources:lib',
        ],
    },
)
