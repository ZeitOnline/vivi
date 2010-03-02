from setuptools import setup, find_packages

setup(
    name='zeit.find',
    version = '0.19.1dev',
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
        'python-cjson',
        'setuptools',
        'zc.iso8601',
        'zeit.cms>1.21',
        'zeit.solr>=0.18.0',
    ],
)
