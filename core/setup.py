from setuptools import setup, find_packages

setup(
    name='zeit.objectlog',
    version='0.3dev',
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
        'ZODB3',
        'pytz',
        'setuptools',
        'zc.sourcefactory',
        'zope.app.keyreference',
        'zope.component',
        'zope.i18n>3.4.0',
        'zope.interface',
        'zope.security',
    ],
    extras_require={
        'test': [
            'zope.securitypolicy',
            'zope.testing',
            'zope.app.zcmlfiles',
            'zope.app.securitypolicy',
        ],
    },
)
