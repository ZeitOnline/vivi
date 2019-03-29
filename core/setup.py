from setuptools import setup, find_packages


setup(
    name='zeit.vgwort',
    version='2.4.2.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="VG Wort SOAP interface",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'grokcore.component',
        'pytest',
        'setuptools',
        'suds',
        'zeit.cms>=3.27.0.dev0',
        'zeit.connector',
        'zeit.content.author',
        'zope.app.generations',
        'zope.component',
        'zope.interface',
        'zope.testing',
    ],
    entry_points=dict(console_scripts=[
        'vgwort-order-tokens=zeit.vgwort.token:order_tokens',
        'vgwort-report=zeit.vgwort.report:report_new_documents',
    ]),
)
