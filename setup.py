from setuptools import setup, find_packages


setup(
    name='zeit.content.author',
    version='2.5.0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de',
    description="vivi Content-Type Author",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit', 'zeit.content'],
    install_requires=[
        'grokcore.component',
        'mock',
        'pysolr',
        'setuptools',
        'zeit.cms>=2.38.0.dev0',
        'zeit.content.image',
        'zeit.edit',
        'zeit.find',
        'zope.annotation',
        'zope.component',
        'zope.interface',
        'zope.testing',
    ],
    entry_points={
        'fanstatic.libraries': [
            'zeit_content_author=zeit.content.author.browser.resources:lib',
        ],
    },
)
