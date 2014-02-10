from setuptools import setup, find_packages

setup(
    name='zeit.newsletter',
    version='0.3',
    author='gocept',
    author_email='mail@gocept.com',
    url='',
    description="""\
""",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages=['zeit'],
    install_requires=[
        'gocept.lxml',
        'gocept.httpserverlayer',
        'gocept.selenium',
        'grokcore.component',
        'mock',
        'pytz',
        'setuptools',
        'zeit.addcentral',
        'zeit.edit',
        'zeit.cms>=2.14.0.dev',
        'zeit.connector',
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
