from setuptools import setup, find_packages


setup(
    name='zeit.content.advertisement',
    version='1.0.0.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi Content-Type Advertisement",
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
        'mock',
        'plone.testing',
        'setuptools',
        'zeit.cms >= 2.55.0.dev0',
        'zeit.content.image',
        'zope.component',
        'zope.formlib',
        'zope.interface',
        'zope.schema',
        'zope.testbrowser',
    ],
    entry_points={
    },
)
