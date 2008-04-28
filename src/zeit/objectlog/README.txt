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

Log something for `content` [#needs-interaction]_:

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
>>> log_entry.principal is None
True
>>> log_entry.time
datetime.datetime(..., tzinfo=<UTC>)
>>> log_entry.message
'Foo'
>>> log_entry.mapping is None
True


When we log another text, we'll get two results. Also, when a principal is
logged in[#login]_ he is logged:

>>> log.log(content, "bar")
>>> result = list(log.get_log(content))
>>> len(result)
2

The order is oldest first:

>>> result[0].message
'Foo'
>>> result[1].message
'bar'
>>> result[1].principal
u'test.hans'


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


Adapting objects to log
-----------------------

There is also an ILog interface which represents the log of one single object:

>>> content_log = zeit.objectlog.interfaces.ILog(content)
>>> content_log
<zeit.objectlog.objectlog.Log object at 0x...>
>>> zope.interface.verify.verifyObject(
...     zeit.objectlog.interfaces.ILog, content_log)
True

We get the same log messages here as when asking the utility directly:

>>> [entry.message for entry in content_log.get_log()]
['Foo', 'bar', 'baz']

We can also create new entries:

>>> content_log.log('bling', dict())
>>> [entry.message for entry in content_log.get_log()]
['Foo', 'bar', 'baz', 'bling']
>>> list(content_log.get_log())[-1].mapping
{}

The log adapter also has an attribute `logs` which is a property of
get_log:

>>> len(content_log.logs)
4
>>> content_log.logs
(<zeit.objectlog.objectlog.LogEntry object at 0x...>, ...)

Note that the `logs` propert is reversed:

>>> content_log.logs[0].message
'bling'


The `logs` property is contrainted with a source:

>>> field = zeit.objectlog.interfaces.ILog['logs']
>>> field = field.bind(content_log)
>>> source = field.value_type.source
>>> len(list(source))
4
>>> list(source)
[<zeit.objectlog.objectlog.LogEntry object at 0x...>, ...]

Verify the titles:

>>> import zope.app.form.browser.interfaces
>>> terms = zope.component.getMultiAdapter(
...     (source, request),
...     zope.app.form.browser.interfaces.ITerms)
>>> term = terms.getTerm(list(source)[0])
>>> zope.i18n.translate(term.title)
u'2008 4 19  10:12:17  [System]: Foo'
>>> term = terms.getTerm(list(source)[1])
>>> zope.i18n.translate(term.title)
u'2008 4 19  10:12:17  [Hans Wurst]: bar'




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
    >>> zope.security.management.newInteraction(request)

.. [#login]

    >>> request.setPrincipal(zope.security.testing.Principal(u'test.hans'))
