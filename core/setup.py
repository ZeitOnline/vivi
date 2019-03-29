from setuptools import setup, find_packages


setup(
    name='zeit.arbeit',
    version='1.2.4',
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
        'plone.testing',
        'zeit.cms>=2.109.0.dev0',
        'zeit.content.article',
        'zeit.content.cp',
        'zeit.content.infobox>=1.25.0.dev0',
        'setuptools',
        'zope.component',
        'zope.interface',
        'zope.schema'
    ],
)
