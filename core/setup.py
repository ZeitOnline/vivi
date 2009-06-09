from setuptools import setup, find_packages

setup(
    name='zeit.find',
    version='0.6dev',
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
        'setuptools',
        'zeit.cms>1.21',
        'python-cjson',
        'pysolr >= 2.0.1',
        'simplejson', # for pysolr
        'zc.iso8601',
    ],
)
