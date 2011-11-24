from setuptools import setup, find_packages

setup(
    name='zeit.content.video',
    version='2.0.4dev',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://svn.gocept.com/repos/gocept-int/zeit.content.video',
    description="""\
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages = ['zeit', 'zeit.content'],
    install_requires=[
        'gocept.form',
        'grokcore.component',
        'setuptools',
        'zeit.cms',
        'zeit.solr',
        'zope.annotation',
        'zope.component',
        'zope.formlib',
        'zope.interface',
        'zope.schema',
    ],
)
