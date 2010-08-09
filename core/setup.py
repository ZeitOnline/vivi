# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from setuptools import setup, find_packages


setup(
    name='zeit.addcentral',
    version='0.2.2dev',
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
        'zeit.cms>=1.28.5',
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
