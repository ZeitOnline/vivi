from setuptools import setup, find_packages

setup(
    name='zeit.seo',
    version='1.4.3dev',
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
        'gocept.form',
        'setuptools',
        'z3c.etestbrowser',
        'zeit.cms>1.4',
        'zeit.connector',
        'zope.app.testing',
        'zope.component',
        'zope.formlib',
        'zope.interface',
        'zope.schema',
    ],
)
