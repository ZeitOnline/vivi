from setuptools import setup, find_packages

setup(
    name = 'zeit.brightcove',
    version='2.6',
    author = 'Christian Zagrodnick',
    author_email = 'cz@gocept.com',
    description = '',
    packages = find_packages('src'),
    package_dir = {'' : 'src'},
    include_package_data = True,
    zip_safe = False,
    namespace_packages = ['zeit'],
    install_requires = [
        'gocept.runner>0.5.3',
        'grokcore.component',
        'grokcore.view',
        'lxml',
        'pytz',
        'setuptools',
        'zeit.addcentral',
        'zeit.cms>=1.54.0.dev0',
        'zeit.content.video',
        'zeit.solr>0.21.0',
        'zope.cachedescriptors',
        'zope.component',
        'zope.interface',
        'zope.schema',
    ],
    entry_points = """
    [console_scripts]
    update-brightcove-repository = zeit.brightcove.update:_update_from_brightcove
    """
)
