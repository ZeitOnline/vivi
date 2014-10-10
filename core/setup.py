from setuptools import setup, find_packages

setup(
    name='zeit.push',
    version='1.6.0.dev0',
    author='gocept',
    author_email='mail@gocept.com',
    url='https://bitbucket.org/gocept/zeit.push',
    description="Sending push notifications through various providers",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages=['zeit'],
    install_requires=[
        'fb',
        'grokcore.component',
        'mock',
        'pytz',
        'requests',
        'setuptools',
        'tweepy',
        'zc.sourcefactory',
        'zeit.cms >= 2.29.0.dev0',
        'zeit.content.article',
        'zeit.objectlog',
        'zope.app.appsetup',
        'zope.component',
        'zope.interface',
        'zope.formlib',
        'zope.schema',
    ],
    entry_points={
        'console_scripts': [
            'facebook-access-token = zeit.push.facebook:create_access_token',
        ],
        'fanstatic.libraries': [
            'zeit_push=zeit.push.browser.resources:lib',
        ],
    },
)
