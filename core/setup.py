from setuptools import setup, find_packages

setup(
    name='zeit.invalidate',
    version = '0.3.5dev',
    author='Christian Zagrodnick',
    author_email='cz@gocept.com',
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
        'zeit.connector>=0.12',
        'zope.app.securitypolicy',
        'zope.app.zcmlfiles',
        'zope.location',
        'zope.publisher',
        'zope.securitypolicy',
        'zope.testing',
        ],
)
