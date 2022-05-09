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
...     print("Resource invalidated: %s" % event.id)
...     print("    %s" % event)
>>> gsm = zope.component.getGlobalSiteManager()
>>> gsm.registerHandler(
...     invalidated,
...     (zeit.connector.interfaces.IResourceInvalidatedEvent,))

Create a log file and attach it to the logging to verify the logging:

>>> from io import StringIO
>>> import logging
>>> log = StringIO()
>>> log_handler = logging.StreamHandler(log)
>>> logging.root.addHandler(log_handler)
>>> old_log_level = logging.root.level
>>> logging.root.setLevel(logging.INFO)


Create a server proxy and bind the invalidate method:

>>> from zeit.cms.webtest import ServerProxy
>>> server = ServerProxy(
...     'http://invalidate:invalidatepw@localhost/', layer['wsgi_app'])
>>> invalidate = getattr(server, '@@invalidate')

When we invalidate an object, the event is issued:

>>> invalidate('http://xml.zeit.de/index')
Resource invalidated: http://xml.zeit.de/index
    <zeit.connector.interfaces.ResourceInvalidatedEvent object at 0x...>
True

The resource id must be a string, a Fault(100) is returned otherwise:

>>> invalidate(27)
Traceback (most recent call last):
    ...
Fault: <Fault 100: "`resource_id` must be string type...


We made one invalidation request which is in the log file. The error is logged
as well:

>>> print(log.getvalue())
zope.invalidate invalidated http://xml.zeit.de/index.
http://localhost/@@invalidate
Traceback (most recent call last):
...Fault: <Fault 100: "`resource_id` must be string type...


We can also invalidate may objects at once using the `invalidate_many` method:

>>> invalidate_many = getattr(server, '@@invalidate_many')

Clear the log:

>>> _ = log.seek(0)

Invalidate several objects at once:

>>> invalidate_many(['index', 'foo', 'bar', 'baz'])
Resource invalidated: index
    <zeit.connector.interfaces.ResourceInvalidatedEvent object at 0x...>
Resource invalidated: foo
    <zeit.connector.interfaces.ResourceInvalidatedEvent object at 0x...>
Resource invalidated: bar
    <zeit.connector.interfaces.ResourceInvalidatedEvent object at 0x...>
Resource invalidated: baz
    <zeit.connector.interfaces.ResourceInvalidatedEvent object at 0x...>
True


>>> invalidate_many('honk')
Traceback (most recent call last):
    ...
Fault: <Fault 100: "`resource_list` must be sequence type...


>>> print(log.getvalue())
zope.invalidate invalidated index.
zope.invalidate invalidated foo.
zope.invalidate invalidated bar.
zope.invalidate invalidated baz.
...


Clean up:

>>> gsm.unregisterHandler(
...     invalidated,
...     (zeit.connector.interfaces.IResourceInvalidatedEvent,))
True
>>> logging.root.removeHandler(log_handler)
>>> logging.root.setLevel(old_log_level)
