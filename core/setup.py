from setuptools import setup, find_packages


setup(
    name='zeit.campus',
    version='1.6.11.dev0',
    author='Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi section Campus",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'grokcore.component',
        'gocept.httpserverlayer',
        'gocept.selenium',
        'mock',
        'plone.testing',
        'setuptools',
        'zeit.cms >= 3.0.dev0',
        'zeit.content.article>=3.25.0.dev0',
        'zeit.content.cp>=3.24.0.dev0',
        'zeit.content.gallery',
        'zeit.content.infobox>=1.25.0.dev0',
        'zeit.content.link',
        'zeit.edit',
        'zeit.push>=1.13.0.dev0',
        'zope.component',
        'zope.interface',
        'zope.schema',
    ],
    entry_points={
        'fanstatic.libraries': [
            'zeit_campus=zeit.campus'
            '.browser.resources:lib',
        ],
    },
)
