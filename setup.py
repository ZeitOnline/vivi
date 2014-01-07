from setuptools import setup, find_packages

setup(
    name='zeit.securitypolicy',
    version='2.1.1',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://code.gocept.com/hg/public/zeit.securitypolicy',
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
        'zeit.brightcove',
        'zeit.calendar',
        'zeit.cms>=1.53dev',
        'zeit.content.article',
        'zeit.content.quiz',
        'zeit.content.rawxml',
        'zeit.content.video',
        'zeit.imp',
        'zeit.invalidate',
        'zeit.seo',
        'zope.app.zcmlfiles',
    ],
)
