from setuptools import setup, find_packages


setup(
    name='zeit.content.volume',
    version='1.2.0.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi Content-Type Volume",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit', 'zeit.content'],
    install_requires=[
        'gocept.form',
        'grokcore.component',
        'lxml',
        'setuptools',
        'zc.sourcefactory',
        'zeit.cms >= 2.90.0.dev0',
        'zeit.content.article >= 3.21.1.dev0',
        'zeit.content.image',
        'zope.component',
        'zope.formlib',
        'zope.interface',
        'zope.schema',
        'zope.security',
    ],
    entry_points={
    },
)
