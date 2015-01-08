from setuptools import setup, find_packages


setup(
    name='zeit.invalidate',
    version='0.3.6.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    description="vivi XML-RPC for DAV invalidations",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'setuptools',
        'zeit.connector>=0.12',
        'zope.app.securitypolicy',
        'zope.app.zcmlfiles',
        'zope.location',
        'zope.publisher',
        'zope.securitypolicy',
        'zope.testing',
    ],
)
