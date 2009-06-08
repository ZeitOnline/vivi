from setuptools import setup, find_packages

setup(
    name='zeit.content.article',
    version='2.0dev',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://svn.gocept.com/repos/gocept-int/zeit.cms/zeit.content.article',
    description="""\
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages = ['zeit', 'zeit.content'],
    install_requires=[
        'gocept.form[formlib]>=0.7.2',
        'gocept.filestore',
        'gocept.lxml>=0.2.1',
        'gocept.mochikit>=1.3.2',
        'gocept.pagelet',
        'iso8601>=0.1.2',
        'lovely.remotetask',
        'lxml>=2.0.2',
        'python-cjson',
        'rwproperty>=1.0',
        'setuptools',
        'sprout',
        'z3c.conditionalviews',
        'z3c.etestbrowser',
        'z3c.flashmessage',
        'z3c.menu.simple>=0.5.1',
        'z3c.traverser',
        'zc.datetimewidget',
        'zc.form',
        'zc.recipe.egg>=1.1.0dev-r84019',
        'zc.relation',
        'zc.resourcelibrary',
        'zc.set',
        'zc.sourcefactory',
        'zc.table',
        'zdaemon',
        'zeit.cms>=1.21.6',
        'zeit.connector>=0.14',
        'zeit.content.infobox',
        'zeit.content.gallery',
        'zeit.content.portraitbox',
        'zeit.objectlog>=0.2',
        'zeit.wysiwyg>1.22',
        'zope.app.apidoc',
        'zope.app.catalog',
        'zope.app.component>=3.4.0b3',
        'zope.app.form>=3.6.0',
        'zope.app.locking',
        'zope.app.onlinehelp',
        'zope.app.preference',
        'zope.app.securitypolicy',
        'zope.app.twisted',
        'zope.copypastemove',
        'zope.i18n>3.4.0',
        'zope.location>=3.4.0b2',
    ],
    entry_points = """
        [console_scripts]
        run-cds-import = zeit.content.article.cds:import_main
        """
)
