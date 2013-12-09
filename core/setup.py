from setuptools import setup, find_packages

setup(
    name='zeit.magazin',
    version='0.1.dev0',
    author='gocept',
    author_email='mail@gocept.com',
    url='',
    description="""\
""",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages=['zeit'],
    install_requires=[
        'grokcore.component',
        'setuptools',
        'zeit.cms>=2.12.0.dev',
        'zope.interface',
        'zope.component',
    ],
)
