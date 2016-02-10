from setuptools import setup, find_packages


setup(
    name='zeit.campus',
    version='1.0.0.dev0',
    author='Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description='Vivi ZCO Content Types',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'grokcore.component',
        'setuptools',
        'zeit.cms>=2.20.0',
        'zeit.content.article>=3.7.0',
        'zeit.content.cp',
        'zeit.content.gallery',
        'zeit.content.link',
        'zope.interface',
        'zope.component',
    ],
)
