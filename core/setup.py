from setuptools import setup, find_packages


setup(
    name='zeit.content.gallery',
    version='2.8.3',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi Content-Type Portraitbox",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit', 'zeit.content'],
    install_requires=[
        'cssselect',
        'Pillow',
        'gocept.form',
        'setuptools',
        'zeit.cms >= 3.0.dev0',
        'zeit.connector>=2.4.0.dev0',
        'zeit.imp>=0.15.0.dev0',
        'zeit.content.image',
        'zeit.push>=1.21.0.dev0',
        'zeit.wysiwyg',
        'zope.app.appsetup',
        'zope.app.testing',
        'zope.component',
        'zope.formlib',
        'zope.interface',
        'zope.publisher',
        'zope.security',
        'zope.testing',
    ],
    entry_points={
        'fanstatic.libraries': [
            'zeit_content_gallery=zeit.content.gallery.browser.resources:lib',
        ],
    },
)
