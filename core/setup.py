from setuptools import setup, find_packages


setup(
    name='zeit.content.infobox',
    version='1.25.1',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi Content-Type Infobox",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit', 'zeit.content'],
    install_requires=[
        'gocept.form',
        'mock',
        'setuptools',
        'zeit.cms>=3.3.0.dev',
        'zeit.wysiwyg',
        'zope.app.appsetup',
        'zope.app.testing',
        'zope.component',
        'zope.formlib',
        'zope.interface',
        'zope.publisher',
        'zope.security',
        'zope.testing',
    ],
)
