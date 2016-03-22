from setuptools import setup, find_packages


setup(
    name='zeit.content.text',
    version='2.0.5.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi Content-Type Text",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit', 'zeit.content'],
    install_requires=[
        'persistent',
        'setuptools',
        'zeit.cms>=2.15.0.dev0',
        'zeit.connector',
        'zope.app.container',
        'zope.app.form',
        'zope.component',
        'zope.formlib',
        'zope.i18n',
        'zope.interface',
        'zope.schema',
        'zope.testbrowser',
    ],
)
