zeit.objectlog
==============

The object log persistently stores information about import changes of an
object.

Setup
-----

>>> import zope.component.hooks
>>> import zope.publisher.browser
>>> import zope.security.management
>>> import zope.security.testing
>>> old_site = zope.component.hooks.getSite()
>>> zope.component.hooks.setSite(getRootFolder())
>>> request = zope.publisher.browser.TestRequest()
>>> zope.security.management.newInteraction(request)


The log can be accessed as utility:

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

>>> from zeit.objectlog.testing import Content

Instanciate and add to the database:

>>> content = Content()
>>> getRootFolder()['content'] = content
>>> import transaction
>>> transaction.commit()

Log something for `content`:

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
logged in, he is logged:

>>> request.setPrincipal(zope.security.testing.Principal(u'test.hans'))
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

When an object is not adaptable to IKeyReference, it's log is always empty:

>>> list(log.get_log(object()))
[]


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


Make sure the log-terms do not break when the principal is deleted:

>>> request.setPrincipal(zope.security.testing.Principal(u'not.there'))
>>> content_log.log('not-there-log')
>>> term = terms.getTerm(list(source)[-1]) 
>>> zope.i18n.translate(term.title)
u'2008 5 27  11:14:46  [not.there]: not-there-log'

Let's make sure the log time is localized to the user's preferred time zone.
Explicitly set a known time:

>>> import pytz
>>> import datetime
>>> entry = list(source)[0]
>>> entry.time = datetime.datetime(2008, 6, 21, 12, 0, tzinfo=pytz.UTC)

What is the peferred time zone? Register an adapter from request to ITZInfo:

>>> import zope.interface.common.idatetime
>>> def tzinfo(request):
...     return pytz.timezone('Europe/Berlin')
>>> sm = zope.component.getSiteManager()
>>> sm.registerAdapter(
...     tzinfo, (zope.interface.Interface,),
...     zope.interface.common.idatetime.ITZInfo)

>>> zope.interface.common.idatetime.ITZInfo(request)
<DstTzInfo 'Europe/Berlin'...>

When we get the title'well have the "corrected" date:

>>> term = terms.getTerm(list(source)[0]) 
>>> zope.i18n.translate(term.title).startswith('2008 6 21  14:00')
True


Processing object logs
======================

So far, we've always obtained complete logs of objects. Sometimes, e.g. for
display in the UI, one wants to process them first, e.g. select only a few
entries. This can be done by registering an ILogProcessor adapter from the
context object in question. This way, application policy for displaying object
logs is not hard-coded into the zeit.objectlog package.

The adapter has a __call__ method that modifies the iterable of log entries if
the log is accessed through the ILog.logs property. Let's create a processor
that reduces the list of log entries to just the last two:

>>> [entry.message for entry in content_log.logs]
['not-there-log', 'bling', 'baz', 'bar', 'Foo']

>>> @zope.component.adapter(Content)
... @zope.interface.implementer(zeit.objectlog.interfaces.ILogProcessor)
... class Processor:
...     def __init__(self, context):
...         pass
...     def __call__(self, entries):
...         return tuple(entries)[-2:]
>>> sm.registerAdapter(Processor)

>>> [entry.message for entry in content_log.logs]
['not-there-log', 'bling']

The adapter does not affect the get_log method:

>>> [entry.message for entry in content_log.get_log()]
['Foo', 'bar', 'baz', 'bling', 'not-there-log']


Cleaning the log
================

The objectlog can be cleaned of old logs.

Cleaning everything that is older than 30 days changes nogthing here:

>>> len(log._object_log)
2
>>> log.clean(datetime.timedelta(days=30))
>>> len(log._object_log)
2

>>> import time
>>> time.sleep(1)
>>> log.clean(datetime.timedelta(seconds=1))
>>> len(log._object_log)
0

Clean up
========

>>> sm.unregisterAdapter(
...     tzinfo, (zope.interface.Interface,),
...     zope.interface.common.idatetime.ITZInfo)
True
>>> sm.unregisterAdapter(Processor)
True
>>> zope.security.management.endInteraction()
>>> zope.component.hooks.setSite(old_site)