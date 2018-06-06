from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))


setup(
    name='zeit.edit',
    version='2.17.1',
    description="Vivi Editor",
    long_description='',
    keywords='',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['zeit'],
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    install_requires=[
        'ZODB',
        'fanstatic',
        'gocept.cache',
        'gocept.httpserverlayer',
        'gocept.lxml',
        'gocept.selenium >= 2.2.0.dev0',
        'grokcore.component',
        'lxml',
        'martian',
        'mock',
        'persistent',
        'setuptools',
        'transaction',
        'xml_compare',
        'zeit.cms>=2.100.0.dev0',
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
