from setuptools import setup, find_packages


setup(
    name='zeit.content.portraitbox',
    version='1.22.16.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='https://svn.gocept.com/repos/gocept-int/zeit.cms',
    description="vivi Content-Type Portraitbox",
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
        'zeit.cms>=2.90.0.dev0',
        'zeit.content.image',
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
