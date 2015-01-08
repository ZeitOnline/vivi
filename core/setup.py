from setuptools import setup, find_packages


setup(
    name='zeit.imp',
    version='0.17.1.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi Image Manipulation Program",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'gocept.httpserverlayer',
        'gocept.selenium>=0.6',
        'setuptools',
        'zeit.cms>=2.15.0.dev0',
        'zeit.content.image>=2.2.0.dev0',
    ],
    entry_points={
        'fanstatic.libraries': [
            'zeit_imp=zeit.imp.browser.resources:lib',
        ],
    },
)
