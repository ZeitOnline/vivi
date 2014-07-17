from setuptools import setup, find_packages

setup(
    name='zeit.securitypolicy',
    version='2.1.4',
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
        'plone.testing',
        'setuptools',
        'xlrd',
        'zeit.brightcove',
        'zeit.calendar',
        'zeit.cms>=2.20.0.dev0',
        'zeit.content.article',
        'zeit.content.image>=2.0.0.dev0',
        'zeit.content.link',
        'zeit.content.quiz',
        'zeit.content.rawxml',
        'zeit.content.text',
        'zeit.content.video',
        'zeit.imp',
        'zeit.invalidate',
        'zeit.seo>=1.6.0.dev0',
        'zope.app.zcmlfiles',
    ],
)
