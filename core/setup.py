from setuptools import setup, find_packages


setup(
    name='zeit.content.rawxml',
    version='0.5.0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="viv Content-Type RawXML",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit', 'zeit.content'],
    install_requires=[
        'setuptools',
        'zeit.cms>=2.31.0.dev0',
        'z3c.etestbrowser',
    ])
