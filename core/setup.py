from setuptools import setup, find_packages

setup(
    name='zeit.securitypolicy',
    version='0.1',
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
        'setuptools',
        'xlrd',
        'zeit.calendar',
        'zeit.cms>1.4',
        'zeit.content.article',
        'zeit.content.quiz',
        'zeit.content.rawxml',
        'zeit.content.video',
        'zeit.invalidate',
        'zeit.seo',
        'zope.app.zcmlfiles',
    ],
)
