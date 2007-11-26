========
ZEIT CMS
========

Create a browser first:

>>> from z3c.etestbrowser.testing import ExtendedTestBrowser
>>> browser = ExtendedTestBrowser()
>>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')


File Listing
============

The filelisting is to be found under /repository. Open it:

>>> browser.open('http://localhost/++skin++cms/repository')

To dive into folder objects we use a Javascript based tree. The testbrowser
doesn't support Javascript unforunately. Therefore we're just opening the url:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01')
>>> print browser.contents
<?xml version...
<!DOCTYPE ...
...Querdax...
...Saarland...
...Saddam...


There is also a View tab:

>>> browser.getLink("View")
<Link text='View'
  url='http://localhost/++skin++cms/repository/online/2007/01/@@view.html'>


Entry Page
==========

The user is redirected to the repository directory listing, if he hits
the site root:

>>> browser.open('http://localhost/++skin++cms/')
>>> print browser.contents
<?xml version...
<!DOCTYPE ...
...online...
...2006...
...2007...


Adding Folders
==============

Folders can be added just like any other content:

>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Folder']
>>> url = menu.value[0]
>>> browser.open(menu.value[0])
>>> browser.getControl("File name").value = 'new-folder'
>>> browser.getControl("Add").click()

After adding a folder we are not at @@edit.html, but on the normal view. In
fact @@edit.html redirects us:

>>> print browser.contents
<?xml version...
<!DOCTYPE ...
...Keine Objekte in diesem Ordner vorhanden...

>>> browser.url
'http://localhost/++skin++cms/repository/new-folder/@@view.html'


Popup file browser
==================

The popup file browser is displayed in a lightbox for selecting objects. It is
reachable at `get_object_browser` for every folder:

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01/'
...              '@@get_object_browser')
>>> print browser.contents
<div id="popup-navtree" class="Tree">
  <ul>
      <li active="True" class="Root">
      ...
</div>
  <div class="objectbrowser-content">
<table class="contentListing">
   ...
</table>
...
</div>
  <div class="tree-view-url">http://localhost/++skin++cms/repository/tree.html</div>

The object browser also supports filtering of types. Without filter everything
is displayed:

>>> browser.open('http://localhost/++skin++cms/repository/'
...              '@@get_object_browser')
>>> print browser.contents
<div id="popup-navtree" class="Tree">
  <ul>
      <li active="True" class="Root">
      ...
</div>
  <div class="objectbrowser-content">
<table class="contentListing">
    ...
   <tbody>
   ...
     <td>
       online
     </td>
     ...
     <td>
       2006
     </td>
     ...
     <td>
       2007
     </td>
     ...
     <td>
       new-folder
     </td>
     ...
     <td>
       Politik
     </td>
     ...
     <td>
       Wirtschaft
     </td>
    ...


Let's filter for folders:


>>> browser.open(
...     'http://localhost/++skin++cms/repository/@@get_object_browser'
...     '?type_filter=zeit.cms.repository.interfaces.IFolder')
>>> print browser.contents
<div id="popup-navtree" class="Tree">
  <ul>
      <li active="True" class="Root">
      ...
</div>
  <div class="objectbrowser-content">
<table class="contentListing">
    ...
   <tbody>
   ...
     <td>
       online
     </td>
     ...
     <td>
       2006
     </td>
     ...
     <td>
       2007
     </td>
     ...
     <td>
       new-folder
     </td>
    ...

>>> 'Politik' in browser.contents
False

To get the initial browsing location the IDefaultBrowsingLocation interface is
used. Do some setup:


>>> import zope.app.component.hooks
>>> old_site = zope.app.component.hooks.getSite()
>>> zope.app.component.hooks.setSite(getRootFolder())
>>>
>>> import zope.component
>>> import zeit.cms.repository.interfaces
>>> import zeit.cms.browser.interfaces
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)

For any type the default browse location will be the folder itself:

>>> location = zope.component.getMultiAdapter(
...     (repository, zeit.cms.interfaces.ICMSContent),
...     zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
>>> location.uniqueId
u'http://xml.zeit.de/'
>>> online = repository['online']
>>> location = zope.component.getMultiAdapter(
...     (online, zeit.cms.interfaces.ICMSContent),
...     zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
>>> location.uniqueId
u'http://xml.zeit.de/online'

For a content object it will be the folder it is contained in:

>>> location = zope.component.getMultiAdapter(
...     (online['2007']['01']['Saarland'], zeit.cms.interfaces.ICMSContent),
...     zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
>>> location.uniqueId
u'http://xml.zeit.de/online/2007/01'


Cleanup:

>>> zope.app.component.hooks.setSite(old_site)
