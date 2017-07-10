from setuptools import setup, find_packages


setup(
    name='zeit.arbeit',
    version='0.1.dev0',
    author='Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi ZAR Content-Type extensions ",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'grokcore.component',
        'zeit.cms',
        'setuptools',
        'zope.component',
        'zope.interface',
    ],
)
