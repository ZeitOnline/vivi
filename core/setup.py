from setuptools import setup, find_packages

setup(
    name='zeit.find',
    version = '/opt/local/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages/Pyrex/Compiler/Errors.py:17:DeprecationWarning:BaseException.messagehasbeendeprecatedasofPython2.6
self.message=message
0.14',
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
        'zeit.solr>=0.3',
    ],
)
