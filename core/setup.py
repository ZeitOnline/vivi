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
        'setuptools',
        'simplejson',
        'zeit.cms',
        'zeit.solr',
        'zope.interface',
        'zope.schema',
    ],
    entry_points = """
    [console_scripts]
    index-videos-and-playlists = zeit.brightcove.solr:index_changed_videos_and_playlists
    """
)
