============
Working Copy
============

The working copy is the area of the CMS where users actually edit content.
Create a test browser first:

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')


When we access our working copy it is created on the fly if it does not exist
yet. So let's open our workingcopy. It doesn't contain any documents, yet:

>>> browser.open('http://localhost/++skin++cms/workingcopy/zope.mgr')
>>> print browser.contents
<?xml version...
<!DOCTYPE ...
Keine ausgecheckten Dokumente...

 
Adding content to the working copy works by checking them out. Let's view the
repository and checkout a document:

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01/Somalia')
>>> print browser.contents
<?xml version...
<!DOCTYPE ...
...namespaces.zeit.de...
...Terrorismus...
...Jochen Stahnke...

Checkout the Somalia Article:

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01/Somalia/checkout')

Checking out redirected us to the document *in* the working copy:

>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.mgr/Somalia/@@view.html'


Looking at our working copy also shows the `Somalia` article:

>>> browser.open('http://localhost/++skin++cms/workingcopy/zope.mgr')
>>> print browser.contents
<?xml version...
<!DOCTYPE ...
...Somalia...


Object browser
==============

When the objectbrowser asks for the default location of a content object in the 
working copy, the answer is relayed to the object in the repository.

We need some setup:

>>> import zope.app.component.hooks
>>> old_site = zope.app.component.hooks.getSite()
>>> zope.app.component.hooks.setSite(getRootFolder())
>>>
>>> import zope.component
>>> import zeit.cms.workingcopy.interfaces
>>> import zeit.cms.browser.interfaces
>>> workingcopy_location = zope.component.getUtility(
...     zeit.cms.workingcopy.interfaces.IWorkingcopyLocation)
>>> workingcopy = workingcopy_location['zope.mgr']

There is no default location for the working copy itself:

>>> zope.component.getMultiAdapter(
...     (workingcopy, zeit.cms.interfaces.ICMSContent),
...     zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
Traceback (most recent call last):
    ...
ComponentLookupError:
    ((<zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>,
      <InterfaceClass zeit.cms.interfaces.ICMSContent>),
     <InterfaceClass zeit.cms.browser.interfaces.IDefaultBrowsingLocation>,
     u'')

For the somalia document we'll get the folder in the repository though:

>>> somalia = workingcopy['Somalia']
>>> location = zope.component.getMultiAdapter(
...     (somalia, zeit.cms.interfaces.ICMSContent),
...     zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
>>> location.uniqueId
u'http://xml.zeit.de/online/2007/01'


When the object does not exist in the repository we're trying to get the
parent. Let's change the uniquyeId of somalia:

>>> somalia.uniqueId = u'http://xml.zeit.de/online/2009/15'

Getting the location will get us to `online` since that is the nearest existing
folder:

>>> location = zope.component.getMultiAdapter(
...     (somalia, zeit.cms.interfaces.ICMSContent),
...     zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
>>> location.uniqueId
u'http://xml.zeit.de/online'


Cleanup:

>>> zope.app.component.hooks.setSite(old_site)

