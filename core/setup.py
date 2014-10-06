from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
NEWS = open(os.path.join(here, 'CHANGES.txt')).read()

setup(
    name='zeit.edit',
    version='2.4.1',
    description="Vivi Editor",
    long_description=README + '\n\n' + NEWS,
    keywords='',
    author='',
    author_email='',
    url='',
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['zeit'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'ZODB',
        'fanstatic',
        'gocept.cache',
        'gocept.httpserverlayer',
        'gocept.lxml',
        'gocept.selenium',
        'grokcore.component',
        'lxml',
        'martian',
        'mock',
        'persistent',
        'setuptools',
        'transaction',
        'zeit.cms>=2.15.0.dev0',
        'zeit.connector',
        'zeit.find>=2.2.dev.0',
        'zope.app.appsetup',
        'zope.app.zcmlfiles',
        'zope.browserpage',
        'zope.component',
        'zope.container',
        'zope.event',
        'zope.formlib',
        'zope.i18n',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.proxy',
        'zope.publisher',
        'zope.schema',
        'zope.security',
        'zope.traversing',
        'zope.viewlet',
    ],
    entry_points={
        'fanstatic.libraries': [
            'zeit_edit=zeit.edit.browser.resources:lib_css',
            'zeit_edit_js=zeit.edit.browser.resources:lib_js',
        ],
    }
)
