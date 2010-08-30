from setuptools import setup, find_packages

setup(
    name='zeit.imp',
    version='0.13.1dev',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://svn.gocept.com/repos/gocept-int/zeit.cms/zeit.imp',
    description="""\
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages = ['zeit'],
    install_requires=[
        'gocept.selenium>=0.6',
        'setuptools',
        'zeit.cms>=1.46dev',
    ],
)
