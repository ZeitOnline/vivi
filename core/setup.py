from setuptools import setup, find_packages

setup(
    name = 'zeit.brightcove',
    version='0.7.0',
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
        'pytz',
        'setuptools',
        'simplejson',
        'zeit.cms>1.44.0',
        'zeit.solr>0.21.0',
        'zope.container',
        'zope.interface',
        'zope.schema',
    ],
    entry_points = """
    [console_scripts]
    update-brightcove-repository = zeit.brightcove.repository:update_repository
    """
)
