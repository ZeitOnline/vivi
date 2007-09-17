from setuptools import setup, find_packages

setup(
    name='zeit.connector',
    version='0.9a2',
    author='Tomas Zerolo, Christian Zagrodnick',
    author_email='tomas@tuxteam.de, cz@gocept.com',
    url='http://trac.gocept.com/zeit',
    description="""\
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages = ['zeit'],
    install_requires=[
        'ZODB3>3.7',
        'gocept.lxml',
        'setuptools',
        'zope.app.appsetup',
        'zope.app.component>=3.4b3',
        'zope.annotation',
        'zope.component',
        'zope.interface',
        'zope.location>=3.4b2',
        'zope.thread',
    ],
    extras_require={
        'test': [
            'zope.testing',
            'zope.app.file',
        ],
    },
)
