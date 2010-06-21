VGWort 
======

Tokens management
+++++++++++++++++


>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> import zeit.vgwort.interfaces
>>> import zope.component
>>> tokens = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)


Load tokens
-----------

>>> import StringIO
>>> csv = StringIO.StringIO("""\
... Öffentlicher Identifikationscode;Privater Identifikationscode
... c0063bcfb7234b35b145af20dccf5e2a;8018af9154bd4b60b0ee4a6891b85583
... 4c47ec781b5b4a288b9a1ab8b2c5ab3c;82e7bb658f75444a9bf74273641f2c29
... 3b787da5b75846e2b39bd814b55a9512;c32e3e163d874e7d8da0d21f96bfeb47
... """)
>>> tokens.load(csv)
>>> len(tokens)
3


Get tokens
----------

Getting tokens is randomized to mostly avoid conflicts.

Seed the random generator with a fixed value to get predictable results:

>>> import random
>>> random.seed(0)
>>> tokens.claim()
('3b787da5b75846e2b39bd814b55a9512', 'c32e3e163d874e7d8da0d21f96bfeb47')
>>> len(tokens)
2
>>> tokens.claim()
('4c47ec781b5b4a288b9a1ab8b2c5ab3c', '82e7bb658f75444a9bf74273641f2c29')
>>> len(tokens)
1
>>> tokens.claim()
('c0063bcfb7234b35b145af20dccf5e2a', '8018af9154bd4b60b0ee4a6891b85583')
>>> len(tokens)
0
>>> tokens.claim()
Traceback (most recent call last):
ValueError: No tokens available.


Token assignment
++++++++++++++++

Tokens are assigned before an object is published.

Mark the test content type:

>>> import zope.interface
>>> import zeit.cms.testcontenttype.testcontenttype
>>> old_implements = list(zope.interface.implementedBy(
...     zeit.cms.testcontenttype.testcontenttype.TestContentType))
>>> zope.interface.classImplements(
...     zeit.cms.testcontenttype.testcontenttype.TestContentType,
...     zeit.vgwort.interfaces.IGenerallyReportableContent)


Add tokens:

>>> tokens.add('public1', 'private1')
>>> tokens.add('public2', 'private2')
>>> tokens.add('public3', 'private3')
>>> len(tokens)
3

The number of available tokens is provided as a view (for Nagios checks):

>>> import zope.testbrowser.testing
>>> browser = zope.testbrowser.testing.Browser()
>>> browser.open('http://localhost/@@zeit.vgwort.available_tokens')
>>> print browser.contents
3

>>> import zeit.cms.interfaces
>>> content = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/testcontent')
>>> zeit.vgwort.interfaces.IGenerallyReportableContent.providedBy(content)
True
>>> import zope.event
>>> import zeit.cms.workflow
>>> zope.event.notify(zeit.cms.workflow.interfaces.BeforePublishEvent(
...     content, content))
>>> len(tokens)
2

When reporting documents we need to know whether an object has already been
reported with VGWort or not. Since the DAV-Server cannot query for the
non-existence of properties, we initialize them with empty values:

>>> info = zeit.vgwort.interfaces.IReportInfo(content)
>>> print info.reported_on
None
>>> info.reported_error
u''
>>> info.reported_error = u'foo'


Publishing the same object again does not assign a new token:

>>> zope.event.notify(zeit.cms.workflow.interfaces.BeforePublishEvent(
...     content, content))
>>> len(tokens)
2

>>> info.reported_error
u'foo'


Tokens are only assigned for the master object of the event:

>>> content2 = zeit.cms.testcontenttype.testcontenttype.TestContentType()
>>> zope.event.notify(zeit.cms.workflow.interfaces.BeforePublishEvent(
...     content2, content))
>>> len(tokens)
2

The private token is *not* synched to xml:

>>> import lxml.etree
>>> print lxml.etree.tostring(content.xml, pretty_print=True),
<testtype>
  <head>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/vgwort" name="public_token">public1</attribute>
  </head>
  <body/>
</testtype>




Clean up
++++++++

Reset marker:

>>> zope.interface.classImplementsOnly(
...     zeit.cms.testcontenttype.testcontenttype.TestContentType,
...     *old_implements)


Restore random-nes: 

>>> random.seed()
