# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from setuptools import setup, find_packages


setup(
    name='zeit.addcentral',
    version='1.1.2.dev0',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://intra.gocept.com/projects/projects/zeit-cms',
    description="""\
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages = ['zeit'],
    install_requires=[
        'gocept.selenium',
        'setuptools',
        'zc.resourcelibrary',
        'zeit.cms>=2.8.0.dev0',
        'zope.app.pagetemplate',
        'zope.browser',
        'zope.cachedescriptors',
        'zope.formlib',
        'zope.interface',
        'zope.publisher',
        'zope.schema',
        'zope.session',
        'zope.viewlet',
    ],
)
