from setuptools import setup, find_packages


setup(
    name='zeit.retresco',
    version='1.0.0.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi interface to retresco keyword and topic management",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'grokcore.component',
        'lxml',
        'mock',
        'plone.testing',
        'requests',
        'setuptools',
        'zeit.cms',
        'zope.component',
        'zope.interface',
        'zope.testbrowser',
    ],
    entry_points={
    },
)
