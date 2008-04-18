zeit.objectlog
==============

The object log persistently stores information about import changes of an
object[#functionaltest]_. The log can be accessed as utility:

>>> import zope.component
>>> import zeit.objectlog.interfaces
>>> log = zope.component.getUtility(
...     zeit.objectlog.interfaces.IObjectLog)
>>> log
<zeit.objectlog.objectlog.ObjectLog object at 0x...>
>>> import zope.interface.verify
>>> zope.interface.verify.verifyObject(
...     zeit.objectlog.interfaces.IObjectLog, log)
True


Create an object for logging. Make it persistent to use the persistent
KeyReference.

>>> import persistent
>>> class Content(persistent.Persistent):
...     pass
>>> __builtins__['Content'] = Content  # to satify persistence

Instanciate and add to the database:

>>> content = Content()
>>> getRootFolder()['content'] = content
>>> import transaction
>>> transaction.commit()

Log something for `content`[#needs-interaction]_:

>>> log.log(content, 'Foo')

Getting the log for `content` yields one log entry:

>>> result = list(log.get_log(content))
>>> len(result)
1
>>> result
[<zeit.objectlog.objectlog.LogEntry object at 0x...>]
>>> log_entry = result[0]

A log entry provides the ILogEntry interface:

>>> zope.interface.verify.verifyObject(
...     zeit.objectlog.interfaces.ILogEntry, log_entry)
True
>>> log_entry.get_object() is content
True
>>> log_entry.principal = u'hans'
>>> log_entry.time
datetime.datetime(..., tzinfo=<UTC>)
>>> log_entry.message
'Foo'
>>> log_entry.mapping is None
True


When we log another text, we'll get two results:

>>> log.log(content, "bar")
>>> result = list(log.get_log(content))
>>> len(result)
2

The order is oldest first:

>>> result[0].message
'Foo'
>>> result[1].message
'bar'


It is possible to pass a mapping to the log which can be used for translating
variables in the message:

>>> log.log(content, "baz", dict(foo='bar'))
>>> result = list(log.get_log(content))
>>> len(result)
3
>>> result[-1].message
'baz'
>>> result[-1].mapping
{'foo': 'bar'}


When we log to another object, the log is obviously seperated:

>>> content2 = Content()
>>> getRootFolder()['c2'] = content2
>>> transaction.commit()
>>> log.log(content2, "change")
>>> result = list(log.get_log(content2))
>>> len(result)
1
>>> result[0].message
'change'



Tear down / Clean up:

>>> del __builtins__['Content']
>>> zope.security.management.endInteraction()
>>> zope.app.component.hooks.setSite(old_site)

.. [#functionaltest] Setup functional test

    >>> import zope.app.component.hooks
    >>> old_site = zope.app.component.hooks.getSite()
    >>> zope.app.component.hooks.setSite(getRootFolder())
    
.. [#needs-interaction] 

    >>> import zope.security.management
    >>> import zope.security.testing
    >>> import zope.publisher.browser
    >>> request = zope.publisher.browser.TestRequest()
    >>> request.setPrincipal(zope.security.testing.Principal(u'hans'))
    >>> zope.security.management.newInteraction(request)
