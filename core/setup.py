from setuptools import setup, find_packages

setup(
    name='zeit.cms',
    version='1.0dev',
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
    namespace_packages = ['zeit', 'zeit.content'],
    install_requires=[
        'PIL',
        'ZODB3>3.7',
        'decorator',
        'gocept.cache',
        'gocept.fckeditor',
        'gocept.form[formlib]>=0.7.2',
        'gocept.lxml',
        'gocept.mochikit>=1.3.2',
        'gocept.pagelet',
        'iso8601>=0.1.2',
        'ldappas>0.6',
        'ldapadapter>=0.7dev-r82228',
        'lxml>1.2',
        'python-cjson',
        'rwproperty>=1.0',
        'setuptools',
        'z3c.flashmessage',
        'z3c.traverser',
        'z3c.zrtresource',
        'z3c.menu.simple>=0.5.1',
        'zc.datetimewidget',
        'zc.form',
        'zc.notification',
        'zc.resourcelibrary',
        'zc.set',
        'zc.sourcefactory',
        'zc.table',
        'zdaemon',
        'zeit.connector>=0.9',
        'zope.location>=3.4.0b2',
        'zope.app.apidoc',
        'zope.app.catalog',
        'zope.app.component>=3.4.0b3',
        'zope.app.locking',
        'zope.app.onlinehelp',
        'zope.app.preference',
        'zope.app.securitypolicy',
        'zope.app.twisted',
        'zope.sendmail',
        'zope.xmlpickle',
    ],
    extras_require={
        'test': [
            'z3c.etestbrowser',
        ],
    },
)
