from setuptools import setup, find_packages

setup(
    name='zeit.vgwort',
    version='2.1.dev0',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://svn.gocept.com/repos/gocept-int/zeit.cms',
    description="""\
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages = ['zeit'],
    install_requires=[
        'grokcore.component',
        'setuptools',
        'suds',
        'unittest2',
        'zeit.cms>=2.0',
        'zeit.connector',
        'zeit.content.author',
        'zope.app.generations',
        'zope.component',
        'zope.interface',
        'zope.testing',
    ],
    entry_points=dict(console_scripts=[
        'vgwort-order-tokens = zeit.vgwort.token:order_tokens',
        'vgwort-report = zeit.vgwort.report:report_new_documents',
        ]),
)
