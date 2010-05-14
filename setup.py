from setuptools import setup, find_packages

setup(
    name='zeit.vgwort',
    version = '0.1.0dev',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://svn.gocept.com/repos/gocept-int/zeit.cms',
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
        'zeit.cms',
        'zope.app.generations',
        'zope.component',
        'zope.interface',
        'zope.testing',
    ],
)
