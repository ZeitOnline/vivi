============
Working Copy
============

The working copy is the area of the CMS where users actually edit content.
Create a test browser first:

>>> from zeit.cms.testing import Browser
>>> browser = Browser(layer['wsgi_app'])
>>> browser.login('user', 'userpw')


When we access our working copy it is created on the fly if it does not exist
yet. So let's open our workingcopy. It doesn't contain any documents, yet:

>>> browser.open('http://localhost/++skin++cms/workingcopy/zope.user')
>>> print(browser.contents)
<?xml version...
<!DOCTYPE ...
No edited documents...


Adding content to the working copy works by checking them out. Let's view the
repository and checkout a document:

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01/Somalia')
>>> print(browser.contents)
<?xml version...
<!DOCTYPE ...
...namespaces.zeit.de...
...Terrorismus...
...Jochen Stahnke...

Checkout the Somalia Article:

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01/Somalia/checkout')

Checking out redirected us to the document *in* the working copy:

>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.user/Somalia/@@view.html'

The sidebar lists the document now:

>>> print(browser.contents)
<...
<div...id="WorkingcopyPanel"...
  <ul class="contentListing">
    <li class="draggable-content type-unknown">
      <img src="...zmi_icon.png"...
      <a href="http://localhost/++skin++cms/workingcopy/zope.user/Somalia/@@edit.html">Somalia</a>
      <span class="uniqueId">http://xml.zeit.de/online/2007/01/Somalia</span>
      ...


The functionality to show the original of a workingcopy was deleted. But it
should still be possible to checkin a workingcopy from an deleted original

>>> bookmark = browser.url
>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01/Somalia/@@delete.html')
>>> browser.getControl('Delete').click()
>>> browser.open(bookmark)
>>> browser.getLink('Checkin').click()

Looking at our working copy also shows the `Somalia` article:

>>> browser.getLink('Checkout').click()
>>> browser.getLink('Edited documents').click()
>>> print(browser.contents)
<?xml version...
<!DOCTYPE ...
...Somalia...

There is a delete link to remove object from the workingcopy again:

>>> browser.getLink('Somalia').click()
>>> browser.getLink('Cancel workingcopy')
<Link text='Cancel workingcopy'
    url='javascript:zeit.cms.lightbox_form('http://localhost/++skin++cms/workingcopy/zope.user/Somalia/@@delete.html')'>

Let's open the delete form:

>>> browser.open(
...     'http://localhost/++skin++cms/workingcopy/zope.user/Somalia/'
...     '@@delete.html')
>>> print(browser.contents)
<div class="topcontent deleteScreen">
  <h1>Delete from workingcopy</h1>
  ...
  <p>
    <span>
      Do you really want to delete your workingcopy?
    </span>
  </p>
  <p class="DeleteItem">
    <img src="http://localhost/++skin++cms/@@/zeit-cms-repository-interfaces-IUnknownResource-zmi_icon.png" alt="UnknownResource" width="20" height="20" border="0" />
    <span>Somalia</span>
    (<span>http://xml.zeit.de/online/2007/01/Somalia</span>)
  </p>
  <form action="http://localhost/++skin++cms/workingcopy/zope.user/Somalia/delete.html"...
    <p>
      <input type="submit" value="Confirm delete" name="form.actions.delete" />
    </p>
  </form>
</div>


Let's delete it:

>>> browser.getControl('Confirm delete').click()
>>> print(browser.contents)
<span class="nextURL">http://localhost/++skin++cms/repository/online/2007/01/Somalia</span>
>>> browser.open('http://localhost/++skin++cms/workingcopy/zope.user')
>>> print(browser.contents)
<?xml ...
      <div id="topcontent">
        <span class="Info">There are no objects in this folder.</span>
      </div>
      ...

Let's try this again, this time marking an article as renameable, which should
be a property of articles just created. Such articles are to be removed from
the repository when they are deleted explicitly from the working copy:

We need some setup:

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()

>>> import zope.component
>>> import zeit.cms.workingcopy.interfaces
>>> import zeit.cms.browser.interfaces
>>> workingcopy_location = zope.component.getUtility(
...     zeit.cms.workingcopy.interfaces.IWorkingcopyLocation)
>>> workingcopy = workingcopy_location['zope.user']

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01/Querdax')
>>> browser.getLink('Checkout').click()
>>> co = next(workingcopy.values())
>>> import zeit.cms.repository.interfaces
>>> zeit.cms.repository.interfaces.IAutomaticallyRenameable(
...     co).renameable = True
>>> browser.open(
...     'http://localhost/++skin++cms/workingcopy/zope.user/Querdax/@@delete.html')
>>> browser.getControl('Confirm delete').click()
>>> print(browser.url)
http://localhost/++skin++cms/workingcopy/zope.user/Querdax/delete.html?form.actions.delete=Confirm+delete
>>> print(browser.contents)
<span class="nextURL">http://localhost/++skin++cms/repository/online/2007/01</span>


Sorting
=======

The sidebar is sorted in a way that the document which was checked out last is
the first. Checkout two documents:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/Somalia')
>>> browser.getLink('Checkout').click()
>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/studiVZ')
>>> browser.getLink('Checkout').click()

>>> print(browser.contents)
<...
  <a href="http://localhost/++skin++cms/workingcopy/zope.user/studiVZ/@@edit.html">studiVZ</a>...
  <a href="http://localhost/++skin++cms/workingcopy/zope.user/Somalia/@@edit.html">Somalia</a>...


Object browser
==============

When the objectbrowser asks for the default location of a content object in the
working copy, the answer is relayed to the object in the repository.

There is no default location for the working copy itself:

>>> import zeit.cms.content.interfaces
>>> source = zope.component.getUtility(
...     zeit.cms.content.interfaces.ICMSContentSource, name='all-types')
>>> zope.component.getMultiAdapter(
...     (workingcopy, source),
...     zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
Traceback (most recent call last):
    ...
ComponentLookupError:...

For the somalia document we'll get the folder in the repository though:

>>> somalia = workingcopy['Somalia']
>>> location = zope.component.getMultiAdapter(
...     (somalia, source),
...     zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
>>> location.uniqueId
'http://xml.zeit.de/online/2007/01/'


When the object does not exist in the repository we're trying to get the
parent. Let's change the uniquyeId of somalia:

>>> somalia.uniqueId = 'http://xml.zeit.de/online/2009/15'

Getting the location will get us to `online` since that is the nearest existing
folder:

>>> location = zope.component.getMultiAdapter(
...     (somalia, source),
...     zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
>>> location.uniqueId
'http://xml.zeit.de/online/'


Cleanup:

>>> import transaction
>>> transaction.abort()


Preview
=======

Open the checked out somalia and change its source:

>>> browser.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...     'Somalia/@@view.html')
>>> browser.getLink('Source').click()
>>> browser.getControl('Document content').value = 'no more!'
>>> browser.getControl('Apply').click()

When we look at the preview now:

>>> browser.follow_redirects = False
>>> browser.getLink('Preview').click()
>>> browser.headers['Location']
'http://localhost/preview-prefix/wcpreview/zope.user/Somalia'

Query arguments are passed to the preview server:

>>> browser.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...     'Somalia/@@view.html')
>>> url = browser.getLink('Preview').url
>>> browser.open(url + '?foo=bar')
>>> browser.headers['Location']
'http://localhost/preview-prefix/wcpreview/zope.user/Somalia?foo=bar'
