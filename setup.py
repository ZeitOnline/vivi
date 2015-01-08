from setuptools import setup, find_packages


setup(
    name='zeit.seo',
    version='1.6.1.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi SEO extensions",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'gocept.form',
        'setuptools',
        'z3c.etestbrowser',
        'zeit.cms>1.4',
        'zeit.connector',
        'zope.app.testing',
        'zope.component',
        'zope.formlib',
        'zope.interface',
        'zope.schema',
    ],
    entry_points={
        'fanstatic.libraries': [
            'zeit_seo=zeit.seo.browser.resources:lib',
        ],
    },
)
