# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from setuptools import setup, find_packages


setup(
    name='zeit.addcentral',
    version='0.1dev',
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
        'setuptools',
        'zc.resourcelibrary',
        'zeit.cms>1.26',
        'zope.app.pagetemplate',
        'zope.cachedescriptors',
        'zope.formlib',
        'zope.interface',
        'zope.schema',
        'zope.viewlet',
    ],
    extras_require=dict(test=[
        'zope.publisher',
    ]),
)
