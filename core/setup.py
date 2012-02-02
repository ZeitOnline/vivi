from setuptools import setup, find_packages

setup(
    name='zeit.content.author',
    version='0.4.1dev',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://code.gocept.com/svn/gocept-int/zeit.cms',
    description="""\
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages = ['zeit', 'zeit.content'],
    install_requires=[
        'grokcore.component',
        'mock',
        'pysolr',
        'setuptools',
        'zeit.cms>1.52.0',
        'zeit.find',
        'zope.annotation',
        'zope.component',
        'zope.interface',
        'zope.testing',
    ],
)
