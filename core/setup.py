from setuptools import setup, find_packages


setup(
    name='zeit.sourcepoint',
    version='1.0.0.dev0',
    author='Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi sourcepoint js download",
    long_description='\n\n'.join(open(name).read() for name in (
        'README.rst',
        'CHANGES.txt',
    )),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'plone.testing',
        'requests',
        'setuptools',
        'zeit.cms',
        'zope.component',
        'zope.interface',
    ],
    entry_points={
        'console_scripts': [
        ]
    },
)
