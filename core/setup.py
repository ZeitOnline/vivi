from setuptools import setup, find_packages

setup(
    name='zeit.find',
    version='2.2.1',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://svn.gocept.com/repos/gocept-int/zeit.find',
    description="""\
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages = ['zeit'],
    install_requires=[
        'gocept.selenium',
        'grokcore.component',
        'setuptools',
        'zc.iso8601',
        'zeit.cms>=2.0',
        'zeit.solr>=2.0',
    ],
)
