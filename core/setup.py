from setuptools import setup, find_packages
import os.path


def project_path(*names):
    return os.path.join(os.path.dirname(__file__), *names)


setup(
    name='zeit.retresco',
    version='1.32.3.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi interface to retresco keyword and topic management",
    long_description='\n\n'.join(open(project_path(name)).read() for name in (
        'README.rst',
        'CHANGES.txt',
    )),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'elasticsearch >=2.0.0, <3.0.0',
        'gocept.runner',
        'grokcore.component',
        'lxml',
        'mock',
        'plone.testing',
        'requests',
        'setuptools',
        'zeit.cms >= 3.28.0.dev0',
        'zeit.content.author',
        'zeit.content.article',
        'zeit.content.gallery',
        'zeit.content.image',
        'zeit.content.infobox',
        'zeit.content.link',
        'zeit.content.portraitbox',
        'zeit.content.rawxml',
        'zeit.content.text',
        'zeit.content.volume',
        'zeit.find >= 3.0.0',
        'zeit.push',
        'zeit.seo',
        'zope.component',
        'zope.dottedname',
        'zope.interface',
        'zope.publisher',
        'zope.testbrowser',
    ],
    entry_points={
        'console_scripts': [
            'update-topiclist=zeit.retresco.connection:update_topiclist',
            'tms-reindex-object=zeit.retresco.update:reindex',
        ]
    },
)
