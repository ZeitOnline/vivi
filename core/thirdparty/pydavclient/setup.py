"""pydavclient is a package which helps in accessing resources published
via the WebDAV protocol. It provides a set of classes which directly
refer to the resource wanted.
"""
from distutils import core

###

_version = '0.2'

_classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: Python Software Foundation License',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Site Management',
    'Topic :: Software Development :: Libraries :: Python Modules'
    ]

###

kw = {}

# If we're running Python 2.3, add extra information
if hasattr(core, 'setup_keywords'):
    if 'classifiers' in core.setup_keywords:
        kw = { 'classifiers':_classifiers }
#

core.setup(name='pydavclient',
           description='WebDAV client classes using libxml2.',
           version=_version,
           url='http://cvs.infrae.com/packages/pydavclient',
           author='Guido Goldstein',
           author_email='gst@infrae.com',
           packages=['dav'],
           maintainer='Guido Goldstein',
           maintainer_email='gst@infrae.com',
           **kw
           )
