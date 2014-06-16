from setuptools import setup, find_packages

setup(
    name='zeit.content.author',
    version='2.2.1.dev0',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://code.gocept.com/svn/gocept-int/zeit.cms',
    description="""\
""",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages=['zeit', 'zeit.content'],
    install_requires=[
        'grokcore.component',
        'mock',
        'pysolr',
        'setuptools',
        'zeit.cms>=2.22.0.dev0',
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
