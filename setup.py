from setuptools import setup, find_packages

setup(
    name='zeit.content.author',
    version='0.1.2dev',
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
        'setuptools',
        'zeit.cms>1.48.0',
        'zope.annotation',
        'zope.component',
        'zope.interface',
        'zope.testing',
    ],
)
