from setuptools import setup, find_packages

setup(
    name='zeit.push',
    version='1.4.1.dev0',
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
        'mock',
        'pytz',
        'requests',
        'setuptools',
        'tweepy',
        'zc.sourcefactory',
        'zeit.cms>=2.23.0.dev0',
        'zeit.content.article>=3.3.0.dev0',
        'zeit.objectlog',
        'zope.component',
        'zope.interface',
    ],
    entry_points={
        'console_scripts': [
            'facebook-access-token = zeit.push.facebook:create_access_token',
        ],
    },
)
