from setuptools import setup, find_packages

setup(
    name='zeit.imp',
    version='0.16.2.dev0',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://svn.gocept.com/repos/gocept-int/zeit.cms/zeit.imp',
    description="""\
""",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages=['zeit'],
    install_requires=[
        'gocept.httpserverlayer',
        'gocept.selenium>=0.6',
        'setuptools',
        'zeit.cms>=2.15.0.dev0',
        'zeit.content.image>=2.2.0.dev0',
    ],
    entry_points={
        'fanstatic.libraries': [
            'zeit_imp=zeit.imp.browser.resources:lib',
        ],
    },
)
