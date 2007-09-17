=========
Connector
=========

Creating a connector::
    
  >>> from pprint import pprint
  >>> from zeit.connector.connector import Connector
  >>> from zeit.connector.cache import resourceCacheFactory
  >>> connector = Connector(u"http://zip4clone.zeit.de:9999/cms/work/")
  >>> connector
  <zeit.connector.connector.Connector object at 0x...>


IConnector Interface
====================

Verify the IConnector interface::

  >>> import zope.interface.verify
  >>> from zeit.connector.interfaces import IConnector
  >>> zope.interface.verify.verifyClass(IConnector, Connector)
  True
  >>> zope.interface.verify.verifyObject(IConnector, connector)
  True


Cache
=====

Set up a site::


    >>> import zope.interface
    >>> import zope.app.component.hooks
    >>> import zope.annotation.attribute
    >>> import zope.annotation.interfaces
    >>> from zope.traversing.interfaces import IContainmentRoot
    >>> from zope.app.component.interfaces import ISite
    >>>
    >>> class Site(object):
    ...     zope.interface.implements(
    ...         ISite, IContainmentRoot,
    ...         zope.annotation.interfaces.IAttributeAnnotatable)
    ...
    ...     def getSiteManager(self):
    ...         return zope.component.getGlobalSiteManager()
    ...
    >>> site = Site()
    >>> old_site = zope.app.component.hooks.getSite()
    >>> zope.app.component.hooks.setSite(site)

And annotations::

    >>> site_manager = zope.app.component.hooks.getSiteManager()
    >>> site_manager.registerAdapter(
    ...     zope.annotation.attribute.AttributeAnnotations,
    ...     (zope.annotation.interfaces.IAttributeAnnotatable,),
    ...     zope.annotation.interfaces.IAnnotations)


The connector needs the ResourceCache, so we register it::

    >>> import zeit.connector.interfaces
    >>>
    >>> site_manager.registerAdapter(
    ...     resourceCacheFactory, 
    ...     (ISite,),
    ...     zeit.connector.interfaces.IResourceCache)


Browsing
========

The browsing interface basically allows listing collections::

  >>> from pprint import pprint
  >>> pprint(list(connector.listCollection((u'http://xml.zeit.de/1998/03'))))
    [(u'plog.txt.19980109.xml', u'http://xml.zeit.de/1998/03/plog.txt.19980109.xml'),
     (u'bulk0398.txt.19980109.xml', u'http://xml.zeit.de/1998/03/bulk0398.txt.19980109.xml'),
     (u'evolution.txt.19980109.xml', u'http://xml.zeit.de/1998/03/evolution.txt.19980109.xml'),
     (u'vor5003.txt.19980109.xml', u'http://xml.zeit.de/1998/03/vor5003.txt.19980109.xml'),
     (u'werkzeug.txt.19980109.xml', u'http://xml.zeit.de/1998/03/werkzeug.txt.19980109.xml'),
     (u'aussteig.txt.19980109.xml', u'http://xml.zeit.de/1998/03/aussteig.txt.19980109.xml'),
     (u'athesen.txt.19980109.xml', u'http://xml.zeit.de/1998/03/athesen.txt.19980109.xml'),
     (u'allianz.txt.19980109.xml', u'http://xml.zeit.de/1998/03/allianz.txt.19980109.xml'),
     (u'wochengr.txt.19980109.xml', u'http://xml.zeit.de/1998/03/wochengr.txt.19980109.xml'),
     (u'jaccuse.txt.19980109.xml', u'http://xml.zeit.de/1998/03/jaccuse.txt.19980109.xml'),
     (u'chabrol.txt.19980109.xml', u'http://xml.zeit.de/1998/03/chabrol.txt.19980109.xml'),
     (u'zm0398.txt.19980109.xml', u'http://xml.zeit.de/1998/03/zm0398.txt.19980109.xml'),
     (u'kosmos.txt.19980109.xml', u'http://xml.zeit.de/1998/03/kosmos.txt.19980109.xml'),
     (u'finis03.txt.19980109.xml', u'http://xml.zeit.de/1998/03/finis03.txt.19980109.xml'),
     (u'kunst.txt.19980109.xml', u'http://xml.zeit.de/1998/03/kunst.txt.19980109.xml'),
     (u'planet0398.txt.19980109.xml', u'http://xml.zeit.de/1998/03/planet0398.txt.19980109.xml'),
     (u'endloes.txt.19980109.xml', u'http://xml.zeit.de/1998/03/endloes.txt.19980109.xml'),
     (u'titel.txt.19980109.xml', u'http://xml.zeit.de/1998/03/titel.txt.19980109.xml'),
     (u'wasserz.txt.19980109.xml', u'http://xml.zeit.de/1998/03/wasserz.txt.19980109.xml'),
     (u'eisangel.txt.19980109.xml', u'http://xml.zeit.de/1998/03/eisangel.txt.19980109.xml'),
     (u'dr03.txt.19980109.xml', u'http://xml.zeit.de/1998/03/dr03.txt.19980109.xml'),
     (u'benjamin.txt.19980109.xml', u'http://xml.zeit.de/1998/03/benjamin.txt.19980109.xml'),
     (u'lohnpol.txt.19980109.xml', u'http://xml.zeit.de/1998/03/lohnpol.txt.19980109.xml'),
     (u'inhalt.txt.19980109.xml', u'http://xml.zeit.de/1998/03/inhalt.txt.19980109.xml'),
     (u'wahl98.txt.19980109.xml', u'http://xml.zeit.de/1998/03/wahl98.txt.19980109.xml'),
     (u'siebeck0398.txt.19980109.xml', u'http://xml.zeit.de/1998/03/siebeck0398.txt.19980109.xml'),
     (u'kinder.txt.19980109.xml', u'http://xml.zeit.de/1998/03/kinder.txt.19980109.xml'),
     (u'wowos.txt.19980109.xml', u'http://xml.zeit.de/1998/03/wowos.txt.19980109.xml'),
     (u'fdp.txt.19980109.xml', u'http://xml.zeit.de/1998/03/fdp.txt.19980109.xml'),
     (u'tvkrit03.txt.19980109.xml', u'http://xml.zeit.de/1998/03/tvkrit03.txt.19980109.xml'),
     (u'horoskop.txt.19980109.xml', u'http://xml.zeit.de/1998/03/horoskop.txt.19980109.xml'),
     (u'thema.txt.19980109.xml', u'http://xml.zeit.de/1998/03/thema.txt.19980109.xml')]

Verify the names for containers are right::

  >>> pprint(list(connector.listCollection(u'http://xml.zeit.de/musik')))
    [(u'archiv', u'http://xml.zeit.de/musik/archiv/'),
     (u'adventskalender', u'http://xml.zeit.de/musik/adventskalender/'),
     (u'box_weblogs', u'http://xml.zeit.de/musik/box_weblogs'),
     (u'channel_themen', u'http://xml.zeit.de/musik/channel_themen'),
     (u'index_alt', u'http://xml.zeit.de/musik/index_alt'),
     (u'soundfiles', u'http://xml.zeit.de/musik/soundfiles/'),
     (u'channel_jazz', u'http://xml.zeit.de/musik/channel_jazz'),
     (u'gebote-der-musikkritik', u'http://xml.zeit.de/musik/gebote-der-musikkritik/'),
     (u'Themenseiten', u'http://xml.zeit.de/musik/Themenseiten/'),
     (u'channel_branche', u'http://xml.zeit.de/musik/channel_branche'),
     (u'channel_klassik', u'http://xml.zeit.de/musik/channel_klassik'),
     (u'unter-cps', u'http://xml.zeit.de/musik/unter-cps/'),
     (u'channel_buecher', u'http://xml.zeit.de/musik/channel_buecher'),
     (u'channel_gross', u'http://xml.zeit.de/musik/channel_gross'),
     (u'channel_bigas', u'http://xml.zeit.de/musik/channel_bigas'),
     (u'channel_blogs', u'http://xml.zeit.de/musik/channel_blogs'),
     (u'musik_test', u'http://xml.zeit.de/musik/musik_test/'),
     (u'genreuebersichten', u'http://xml.zeit.de/musik/genreuebersichten/'),
     (u'channel_magazin', u'http://xml.zeit.de/musik/channel_magazin'),
     (u'channel_musik', u'http://xml.zeit.de/musik/channel_musik'),
     (u'channel_geschichte', u'http://xml.zeit.de/musik/channel_geschichte'),
     (u'index_alt_05_2007', u'http://xml.zeit.de/musik/index_alt_05_2007'),
     (u'channel_serien', u'http://xml.zeit.de/musik/channel_serien'),
     (u'index', u'http://xml.zeit.de/musik/index'),
     (u'channel_speziell', u'http://xml.zeit.de/musik/channel_speziell')]

Resources
=========


Get an object. We will get a cached resource::

    >>> index_id = "http://xml.zeit.de/deutschland/index"
    >>> ressource = connector[index_id]
    >>> ressource
    <zeit.connector.resource.CachedResource object at 0x...>
    >>> print ressource.data.read()
    <?xml ...
    <centerpage ...


If a resource does not exist, a KeyError is raised::

  >>> connector['http://xml.zeit.de/foobar']
  Traceback (most recent call last):
    ...
  KeyError: "The resource 'http://xml.zeit.de/foobar' does not exist."

The properties are cached now::

    >>> cache = zeit.connector.interfaces.IResourceCache(site)
    >>> properties = cache.properties[index_id]
    >>> properties[('getcontenttype', 'DAV:')]
    'text/xml'


We can also get directory resources::

    >>> resource = connector['http://xml.zeit.de/deutschland/']
    >>> resource.type
    'collection'

Storing an object. The object will be created when not yet there.
Don't forget content-type::

    >>> import StringIO
    >>> from zeit.connector.resource import Resource
    >>> res = Resource('http://xml.zeit.de/testing/conn1',
    ...                'conn1',
    ...                'text',
    ...                StringIO.StringIO('Pop goes the weasel!'),
    ...                contentType = 'text/plain')
    >>> connector.add(res)

We've set `text` as resource type. We should get `text` back, when getting the
resource::

    >>> connector[res.id].type
    'text'

Resources may be locked (NOTE: the time argument in lock is currently ignored,
TBD)::

    >>> from datetime import datetime, timedelta
    >>> connector.locked('http://xml.zeit.de/testing/conn1')
    (None, None, False)
    >>> token = connector.lock('http://xml.zeit.de/testing/conn1',
    ...                        'http://xml.zeit.de/users/frodo',
    ...                        datetime.today() + timedelta(hours=2))
    >>> connector.locked('http://xml.zeit.de/testing/conn1')
    (u'http://xml.zeit.de/users/frodo',
     datetime.datetime(9999, 12, 31, 23, 59, 59, 999999),
     True)

To unlock it, you would have to supply the locktoken. The library takes
care of that (hmmm?)::
    >>> connector.unlock('http://xml.zeit.de/testing/conn1')
    >>> connector.locked('http://xml.zeit.de/testing/conn1')
    (None, None, False)

The object can be also stored dictionary-style::

    >>> res.data = StringIO.StringIO("Round and round the cobbler's bench")
    >>> connector["http://xml.zeit.de/testing/conn2"] = res

Resources also have properties, which can be set/changed/unset,
always indexed by a namespace/name pair.
Note: name comes first -- don't ask me why::

    >>> token = connector.lock('http://xml.zeit.de/testing/conn3',
    ...                        'http://xml.zeit.de/users/frodo',
    ...                        datetime.today() + timedelta(hours=2))
    >>> res.data = StringIO.StringIO("Mary had a little lamb")
    >>> res.properties[('colour', 'http://namespaces.zeit.de/test')] = (
    ...     'bright blue')
    >>> connector["http://xml.zeit.de/testing/conn3"] = res

The properties and data are stored on the server now. Get the resource again::

    >>> res = connector["http://xml.zeit.de/testing/conn3"]
    >>> res.properties[('colour', 'http://namespaces.zeit.de/test')]
    'bright blue'
    >>> res.data.read()
    'Mary had a little lamb'

We can change properties explicitly using `changeProperties`::

    >>> connector.changeProperties(
    ...     'http://xml.zeit.de/testing/conn3',
    ...     {('colour', 'http://namespaces.zeit.de/test'): u'gr\xfcn'})
    >>> res = connector["http://xml.zeit.de/testing/conn3"]
    >>> res.properties[('colour', 'http://namespaces.zeit.de/test')]
    u'gr\xfcn'


Unlock the resource again::

    >>> connector.unlock('http://xml.zeit.de/testing/conn3')

Delete the resource::

    >>> del connector["http://xml.zeit.de/testing/conn3"]



Collections
===========

Creating collections works like creating any other resource. Create a resource
object first::

    >>> collection_id = 'http://xml.zeit.de/testing/collection/'
    >>> coll = zeit.connector.resource.Resource(
    ...     collection_id, 'collection', 'collection', StringIO.StringIO(''))

Add the collection rssource to the dav and see we get it back::

    >>> connector.add(coll)
    >>> res = connector[collection_id]
    >>> res.type
    'collection'

Initially a collection is empty::

    >>> list(connector.listCollection(collection_id))
    []


Remove the collection again::

    >>> del connector[collection_id]


Search (interface only)::
=========================

The building blocks are search vars:

    >>> from zeit.connector.search import SearchVar
    >>> author = SearchVar('author', 'http://namespaces.zeit.de/document/')
    >>> volume = SearchVar('volume', 'http://namespaces.zeit.de/document/')
    >>> year = SearchVar('year', 'http://namespaces.zeit.de/document/')
    >>> month = SearchVar('month', 'http://namespaces.zeit.de/document/')
    >>> ressort = SearchVar('ressort', 'http://namespaces.zeit.de/document/')

Queries are built of basic terms involving search vars stitched together into expressions:

    >>> connector.search([author, volume], (year > '1997') & ((month == '07') | (month == '08')) & (ressort == 'Leben'))
  
Clean up
========

Cleanup after ourselves::

    >>> site_manager.unregisterAdapter(
    ...     resourceCacheFactory,
    ...     (ISite,),
    ...     zeit.connector.interfaces.IResourceCache)
    True
    >>> site_manager.unregisterAdapter(
    ...     zope.annotation.attribute.AttributeAnnotations,
    ...     (zope.annotation.interfaces.IAttributeAnnotatable,),
    ...     zope.annotation.interfaces.IAnnotations)
    True
    >>> zope.app.component.hooks.setSite(old_site)
