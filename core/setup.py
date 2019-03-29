from setuptools import setup, find_packages


setup(
    name='zeit.push',
    version='1.28.3.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="Sending push notifications through various providers",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'bugsnag',
        'fb',
        'gocept.testing',
        'grokcore.component',
        'mock',
        'pytz',
        'requests',
        'setuptools',
        'tweepy',
        'urbanairship >= 1.0',
        'zc.sourcefactory',
        'zeit.cms >= 3.13.0.dev0',
        'zeit.content.article',
        'zeit.content.image',
        'zeit.content.text>=2.2.0.dev0',
        'zeit.objectlog',
        'zope.app.appsetup',
        'zope.component',
        'zope.formlib',
        'zope.interface',
        'zope.schema',
    ],
    entry_points={
        'console_scripts': [
            'facebook-access-token = zeit.push.facebook:create_access_token',
            'ua-payload-doc = zeit.push.urbanairship:print_payload_documentation',
        ],
        'fanstatic.libraries': [
            'zeit_push=zeit.push.browser.resources:lib',
        ],
    },
)
