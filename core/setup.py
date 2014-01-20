from setuptools import setup, find_packages

setup(
    name='zeit.magazin',
    version='1.0.1',
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
        'gocept.selenium',
        'gocept.testing>=1.4.0.dev0',
        'grokcore.component',
        'setuptools',
        'zc.form',
        'zeit.cms>=2.13.0.dev0',
        'zeit.content.article>=3.1.0.dev0',
        'zeit.content.portraitbox',
        'zeit.edit',
        'zope.interface',
        'zope.component',
    ],
)
