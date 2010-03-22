from setuptools import setup, find_packages

setup(
    name = 'zeit.brightcove',
    version = '0.1.0dev',
    author = 'Christian Zagrodnick',
    author_email = 'cz@gocept.com',
    description = '',
    packages = find_packages('src'),
    package_dir = {'' : 'src'},
    include_package_data = True,
    zip_safe = False,
    namespace_packages = ['zeit'],
    install_requires = [
        'lxml',
        'setuptools',
        'simplejson',
        'zeit.cms>1.41.0',
        'zeit.solr',
        'zope.container',
        'zope.interface',
        'zope.schema',
    ],
    entry_points = """
    [console_scripts]
    index-videos-and-playlists = zeit.brightcove.solr:index_changed_videos_and_playlists
    """
)
