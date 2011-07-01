from setuptools import setup, find_packages

setup(
    name='zeit.newsletter',
    version='0.1dev',
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
        'gocept.lxml',
        'gocept.selenium',
        'grokcore.component',
        'mock',
        'pytz',
        'setuptools',
        'zeit.addcentral',
        'zeit.edit',
        'zeit.cms',
        'zeit.connector',
        'zope.interface',
        'zope.component',
        'zope.container',
    ],
)
