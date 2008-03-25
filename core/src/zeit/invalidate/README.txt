==========
Invalidate
==========

The backend can notify the CMS about resource which have changed in the
backend. It does this by calling the `invalidate` method on the CMS.

Internally we need to produce a `zeit.connector.IResourceInvalidatedEvent` to
invalidate the resource. Create a test handler:

>>> import zope.component
>>> import zeit.connector.interfaces
>>> def invalidated(event):
...     print "Resource invalidated:", event.id
...     print "   ", event
>>> gsm = zope.component.getGlobalSiteManager()
>>> gsm.registerHandler(
...     invalidated,
...     (zeit.connector.interfaces.IResourceInvalidatedEvent,))

Create a log file and attach it to the logging to verify the logging:

>>> import logging
>>> import StringIO
>>> log = StringIO.StringIO()
>>> log_handler = logging.StreamHandler(log)
>>> logging.root.addHandler(log_handler)
>>> old_log_level = logging.root.level
>>> logging.root.setLevel(logging.INFO)


Create a server proxy and bind the invalidate method:

>>> from zope.app.testing.xmlrpc import ServerProxy
>>> server = ServerProxy('http://invalidate:invalidatepw@localhost/')
>>> invalidate = getattr(server, '@@invalidate')

When we invalidate an object, the event is issued:

>>> invalidate('http://xml.zeit.de/index')
Resource invalidated: http://xml.zeit.de/index
    <zeit.connector.interfaces.ResourceInvaliatedEvent object at 0x...>


The resource id must be a string, a Fault(100) is returned otherwise:

>>> invalidate(27)
Traceback (most recent call last):
    ...
Fault: <Fault 100: "`resource_id` must be string type, got <type 'int'>">


We made one invalidation request which is in the log file:

>>> print log.getvalue()
zope.invalidate invalidated http://xml.zeit.de/index.


Clean up:

>>> gsm.unregisterHandler(
...     invalidated,
...     (zeit.connector.interfaces.IResourceInvalidatedEvent,))
True
>>> logging.root.removeHandler(log_handler)
>>> logging.root.setLevel(old_log_level)
