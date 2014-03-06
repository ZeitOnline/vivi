from setuptools import setup, find_packages

setup(
    name='zeit.content.text',
    version='2.0.0.dev0',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://svn.gocept.com/repos/gocept-int/zeit.cms',
    description="ZEIT Text",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages=['zeit', 'zeit.content'],
    install_requires=[
        'ZODB3',
        'setuptools',
        'zeit.cms>=2.15.0.dev0',
        'zeit.connector',
        'zope.app.container',
        'zope.app.form',
        'zope.component',
        'zope.formlib',
        'zope.i18n',
        'zope.interface',
        'zope.schema',
    ],
)
