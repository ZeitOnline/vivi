============
Working Copy
============

The working copy is the area of the CMS where users actually edit content.
Create a test browser first:

>>> from z3c.etestbrowser.testing import ExtendedTestBrowser
>>> browser = ExtendedTestBrowser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')


When we access our working copy it is created on the fly if it does not exist
yet. So let's open our workingcopy. It doesn't contain any documents, yet:

>>> browser.open('http://localhost/++skin++cms/workingcopy/zope.user')
>>> print browser.contents
<?xml version...
<!DOCTYPE ...
No edited documents...

 
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
'http://localhost/++skin++cms/workingcopy/zope.user/Somalia/@@view.html'

The sidebar lists the document now:

>>> print browser.contents
<?xml ...
<!DOCTYPE html ...
  <tbody>
  <tr>
    <td>
      <img src="http://localhost/++skin++cms/@@/zeit-cms-repository-interfaces-IUnknownResource-zmi_icon.png" alt="UnknownResource" width="20" height="20" border="0" />
    </td>
    <td>
      <a href="http://localhost/++skin++cms/workingcopy/zope.user/Somalia/edit.html">Somalia</a>
    </td>
  </tr>
  </tbody>
</table>
...


Looking at our working copy also shows the `Somalia` article:

>>> browser.open('http://localhost/++skin++cms/workingcopy/zope.user')
>>> print browser.contents
<?xml version...
<!DOCTYPE ...
...Somalia...

There is a delete link to remove object from the workingcopy again:

>>> browser.getLink('Somalia').click()
>>> browser.getLink('Delete', index=1)
<Link text='[IMG] Delete'
    url="javascript:zeit.cms.lightbox_form('http://localhost/++skin++cms/workingcopy/zope.user/Somalia/@@deletecontent.html')">

Let's open the delete form:

>>> browser.open(
...     'http://localhost/++skin++cms/workingcopy/zope.user/Somalia/'
...     '@@deletecontent.html')
>>> print browser.contents
<div class="topcontent deleteScreen">
  <h1>Delete content</h1>
  <p>
    <span>
      Do you really want to delete the object from the folder
      "<span class="containerName">zope.user</span>"?
    </span>
  </p>
  <p class="DeleteItem">
    <img src="http://localhost/++skin++cms/@@/zeit-cms-repository-interfaces-IUnknownResource-zmi_icon.png" alt="UnknownResource" width="20" height="20" border="0" />
    <span>Somalia</span>
    (<span>http://xml.zeit.de/online/2007/01/Somalia</span>)
  </p>
<BLANKLINE>
<BLANKLINE>
  <form action="http://localhost/++skin++cms/workingcopy/zope.user/Somalia/deletecontent.html">
    <p>
      <input type="submit" value="Delete" name="delete" />
    </p>
  </form>
</div>


Let's delete it:

>>> browser.getControl('Delete').click()
>>> print browser.contents
<?xml ...
      <div id="topcontent">
        <span class="Info">
          There are no objects in this folder.
        </span>
      </div>
      ...


Object browser
==============

When the objectbrowser asks for the default location of a content object in the 
working copy, the answer is relayed to the object in the repository.


Checkout the somalia article again:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/Somalia')
>>> browser.getLink('Checkout').click()


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
>>> workingcopy = workingcopy_location['zope.user']

There is no default location for the working copy itself:

>>> import zeit.cms.content.interfaces
>>> source = zope.component.getUtility(
...     zeit.cms.content.interfaces.ICMSContentSource, name='all-types')
>>> zope.component.getMultiAdapter(
...     (workingcopy, source),
...     zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
Traceback (most recent call last):
    ...
ComponentLookupError:
    ((<zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>,
      <zeit.cms.content.contentsource.CMSContentSource object at 0x...>),
     <InterfaceClass zeit.cms.browser.interfaces.IDefaultBrowsingLocation>,
     u'')

For the somalia document we'll get the folder in the repository though:

>>> somalia = workingcopy['Somalia']
>>> location = zope.component.getMultiAdapter(
...     (somalia, source),
...     zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
>>> location.uniqueId
u'http://xml.zeit.de/online/2007/01'


When the object does not exist in the repository we're trying to get the
parent. Let's change the uniquyeId of somalia:

>>> somalia.uniqueId = u'http://xml.zeit.de/online/2009/15'

Getting the location will get us to `online` since that is the nearest existing
folder:

>>> location = zope.component.getMultiAdapter(
...     (somalia, source),
...     zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
>>> location.uniqueId
u'http://xml.zeit.de/online'


Cleanup:

>>> zope.app.component.hooks.setSite(old_site)


Preview
=======

The preview expects the preview container to exist, so create it. `tmp` first:

>>> browser.open('http://localhost/++skin++cms/')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Folder']
>>> browser.open(menu.value[0])
>>> browser.getControl("File name").value = 'tmp'
>>> browser.getControl("Add").click()

Create `previews` now:

>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Folder']
>>> browser.open(menu.value[0])
>>> browser.getControl("File name").value = 'previews'
>>> browser.getControl("Add").click()

Open the checked out somalia and change its source:


>>> browser.open('http://localhost/++skin++cms/workingcopy/zope.user/Somalia/@@view.html')
>>> browser.getLink('Source').click()
>>> browser.getControl('Document content').value = 'no more!'
>>> browser.getControl('Apply').click()

When we look at the preview now, we will be redirected:

>>> import zeit.cms.testing
>>> zeit.cms.testing.click_wo_redirect(browser, 'Preview')
HTTP Error 303: See Other
http://localhost/preview-prefix/tmp/previews/...

Retrieve the copied object:

>>> browser.open('http://localhost/++skin++cms/repository/tmp/previews/')
>>> url = browser.etree.xpath(
...     '//table[contains(@class, "contentListing")]'
...     '//span[@class="URL"]')[0].text
>>> browser.open(url)
>>> print browser.contents
<?xml ...
    <pre>no more...
