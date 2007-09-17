=========
Connector
=========

Small test herness for cconnector::
    
    >>> from pprint import pprint
    >>> from zeit.connector.connector import Connector
    >>> connector = Connector("http://localhost/cms/work")
    >>> connector
    <zeit.connector.connector.Connector object at 0x...>


Browsing
========

The browsing interface basically allows listing collections::

  >>> from pprint import pprint
  >>> pprint(list(connector.listCollection(('', ))))
  [(u'2006', u'http://xml.zeit.de/2006'),
   (u'2007', u'http://xml.zeit.de/2007'),
   (u'online', u'http://xml.zeit.de/online'),
   (u'politik.feed', u'http://xml.zeit.de/politik.feed'),
   (u'wirtschaft.feed', u'http://xml.zeit.de/wirtschaft.feed')]

  >>> entry = list(connector.listCollection(('', 'online', '2007', '01')))[0]
  >>> print entry
  (u'4schanzentournee-abgesang',
   u'http://xml.zeit.de/online/2007/01/4schanzentournee-abgesang')


Getting Resources
=================

Resources are retrieved by their unique ids. We retrieve the 4schzentournee read
above::

  >>> unique_id = entry[1]
  >>> resource = connector[unique_id]
  >>> resource
  <zeit.cms.connector.Resource object at 0x...>

  >>> resource.id
  u'http://xml.zeit.de/online/2007/01/4schanzentournee-abgesang'


Locking and Unlocking
=====================

Users can lock and unlock content. We continue to use the 4schanzentournee
resource. For that we need a principal and a target date::

  >>> import datetime
  >>> from zope.security.testing import Principal
  >>> hans = Principal('hans')
  >>> until = datetime.datetime.now() + datetime.timedelta(days=1)


Before we acquire the lock, the resource is not locked::

  >>> connector.locked(unique_id)
  (None, None)


After locking the resource is locked::

  >>> connector.lock(unique_id, hans, until)
  >>> locked_for, locked_until = connector.locked(unique_id)
  >>> locked_for.id
  'hans'
  >>> locked_until
  datetime.datetime(...)


Note that hans has locked the resource. Dieter can override the lock::
  
  >>> dieter = Principal('dieter')
  >>> connector.lock(unique_id, dieter, until)
  >>> locked_for, locked_until = connector.locked(unique_id)
  >>> locked_for.id
  'dieter'



Adding Content to the Repository
================================

Item Assignment
+++++++++++++++

Adding content or changing works by item assignement to the connector. The key
is the unique Id of the object. Create a resource first::

  >>> from zeit.cms.connector import Resource
  >>> resource = Resource('/online/2007/02/Seehofer', 'Seehofer',
  ...                     'unkown', 'Seehofer schlaegt zurueck')

Let's have a look into the collection `/online/2007/01`. It is empty so far::

  >>> list(connector.listCollection(('', 'online', '2007', '02')))
  []


Add the `resource` to the connector::

  >>> connector[resource.id] = resource

We now can get the object back from the connector::

  >>> resource_2 = connector[resource.id]
  >>> print resource_2.data
  Seehofer schlaegt zurueck

Also the collection contains the resource now::

  >>> list(connector.listCollection(('', 'online', '2007', '02')))
  [(u'Seehofer', u'http://xml.zeit.de/online/2007/02/Seehofer')]


Add Method
++++++++++

Since the connector knows very well how to get the unique id from resource
objects there is a convinience method called `add`. So let's create another
resource and add id using the `add` method::

  >>> resource = Resource(
  ...     'http://xml.zeit.de/online/2007/02/DaimlerChrysler',
  ...     'DaimlerChrysler', 'unkown', 'Zwischen Angst und Schock')
  >>> connector.add(resource)

  >>> from pprint import pprint
  >>> pprint(list(connector.listCollection(('', 'online', '2007', '02'))))
  [(u'DaimlerChrysler', u'http://xml.zeit.de/online/2007/02/DaimlerChrysler'),
   (u'Seehofer', u'http://xml.zeit.de/online/2007/02/Seehofer')]


Removing Content From the Repository
====================================

Removing words via the normal __delitem__ mechanismns. Let's look what we have
first::

  >>> pprint(list(connector.listCollection(('', ))))
  [(u'2006', u'http://xml.zeit.de/2006'),
   (u'2007', u'http://xml.zeit.de/2007'),
   (u'online', u'http://xml.zeit.de/online'),
   (u'politik.feed', u'http://xml.zeit.de/politik.feed'),
   (u'wirtschaft.feed', u'http://xml.zeit.de/wirtschaft.feed')]

After remove the `politik.feed` it is also gone from the listing::

  >>> del connector['http://xml.zeit.de/politik.feed']
  >>> pprint(list(connector.listCollection(('', ))))
  [(u'2006', u'http://xml.zeit.de/2006'),
   (u'2007', u'http://xml.zeit.de/2007'),
   (u'online', u'http://xml.zeit.de/online'),
   (u'wirtschaft.feed', u'http://xml.zeit.de/wirtschaft.feed')]

    
