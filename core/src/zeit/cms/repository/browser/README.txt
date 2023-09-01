========
ZEIT CMS
========

Create a browser first:

>>> from zeit.cms.testing import Browser
>>> browser = Browser(layer['wsgi_app'])
>>> browser.login('user', 'userpw')


File Listing
============

The filelisting is to be found under /repository. Open it:

>>> browser.open('http://localhost/++skin++cms/repository')

To dive into folder objects we use a Javascript based tree. The testbrowser
doesn't support Javascript unforunately. Therefore we're just opening the url:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01')
>>> print(browser.contents)
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
>>> print(browser.url)
http://localhost/++skin++cms/repository/online/2008/26


Adding Folders
==============

Folders can be added just like any other content:

>>> browser.open('http://localhost/++skin++cms/repository')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Folder']
>>> url = menu.value[0]
>>> browser.open(menu.value[0])
>>> browser.getControl("File name").value = 'new-folder'
>>> browser.getControl("Add").click()

After adding a folder we are not at @@edit.html, but on the normal view. In
fact @@edit.html redirects us:

>>> print(browser.contents)
<?xml version...
<!DOCTYPE ...
  ...There are no objects in this folder...

>>> browser.url
'http://localhost/++skin++cms/repository/new-folder/@@view.html'


Note that folders also cannot be checked out. This is not a technical
limitation but a choice since folders do not have any metadata right now, there
is nothing a user could do when checking out a folder:

>>> browser.getLink('Checkout')
Traceback (most recent call last):
    ...
LinkNotFoundError

Folders have a metadata page which shows the folder contents:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/new-folder/'
...     '@@metadata_preview')
>>> print(browser.contents)
 <div class="contextViewsAndActions">
  <div class="context-views">
  ...
    <div class="folder-length">
      0 Entries
    </div>
    <ul class="folder-contents">
    </ul>
    ...


Popup file browser
==================

The popup file browser is displayed in a lightbox for selecting objects. It is
reachable at `get_object_browser` for every folder:

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01/'
...              '@@get_object_browser')
>>> print(browser.contents)
  <h1>http://xml.zeit.de/online/2007/01/</h1>
  <div id="popup-navtree" class="Tree">
  <ul>
      <li active="True" class="Root...">
      ...
</div>
  <div class="objectbrowser-content">
<table class="contentListing hasMetadata">
   ...
</table>
...
</div>
  <div class="tree-view-url">http://localhost/++skin++cms/repository/@@tree.html</div>
...

The object browser also supports filtering of types via a content type source
name. Without filter everything is displayed:

>>> browser.open('http://localhost/++skin++cms/repository/'
...              '@@get_object_browser')
>>> print(browser.contents)
  <h1>http://xml.zeit.de/</h1>
<div id="popup-navtree" class="Tree">
  <ul>
      <li active="True" class="Root...">
      ...
</div>
  <div class="objectbrowser-content">
<table class="contentListing hasMetadata">
    ...
   <tbody>
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
       ...testcontent...
     </td>
     ...


Let's filter for folders:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/@@get_object_browser'
...     '?type_filter=folders')
>>> print(browser.contents)
  <h1>http://xml.zeit.de/</h1>
<div id="popup-navtree" class="Tree">
  <ul>
      <li active="True" class="Root...">
      ...
</div>
  <div class="objectbrowser-content">
<table class="contentListing hasMetadata">
    ...
   <tbody>
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

>>> 'testcontent' in browser.contents
False

When there are no suitable objects, we'll get a message:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/'
...     '@@get_object_browser?type_filter=folders')
>>> print(browser.contents)
  <h1>http://xml.zeit.de/online/2007/01/</h1>
  ...
  <div class="objectbrowser-content no-content">
    There are no selectable objects in this folder.
  </div>
  ...


Within the object browser the tree is automatically expanded:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/'
...     '@@get_object_browser')
>>> print(browser.contents)
  <h1>http://xml.zeit.de/online/2007/01/</h1>
  ...
      <li action="collapse" active="True" class="NotRoot..."
          uniqueid="http://xml.zeit.de/online/2007/01/">
          ...


To get the initial browsing location the IDefaultBrowsingLocation interface is
used. Do some setup:

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> import zope.component
>>> import zeit.cms.repository.interfaces
>>> import zeit.cms.browser.interfaces
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)

For any type the default browse location will be the folder itself:

>>> import zeit.cms.content.interfaces
>>> source = zope.component.getUtility(
...     zeit.cms.content.interfaces.ICMSContentSource, name='all-types')
>>> location = zope.component.getMultiAdapter(
...     (repository, source),
...     zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
>>> location.uniqueId
'http://xml.zeit.de/'
>>> online = repository['online']
>>> location = zope.component.getMultiAdapter(
...     (online, source),
...     zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
>>> location.uniqueId
'http://xml.zeit.de/online/'

For a content object it will be the folder it is contained in:

>>> location = zope.component.getMultiAdapter(
...     (online['2007']['01']['Saarland'], source),
...     zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
>>> location.uniqueId
'http://xml.zeit.de/online/2007/01/'


There is a view all ICMSContent which redirects to the browsing location:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/'
...     '@@default-browsing-location?type_filter=all-types')
>>> print(browser.url)
http://localhost/++skin++cms/repository/online/2007/01/@@get_object_browser?type_filter=all-types



Viewing objects by unique_id
============================

There is a helper which redirects to the view of an object when you put in
the unique id:

>>> browser.open('http://localhost/++skin++cms/@@redirect_to?unique_id='
...              'http://xml.zeit.de/online/2007/01/Somalia')
>>> browser.url
'http://localhost/++skin++cms/repository/online/2007/01/Somalia/'

When another view is desired it can be passed as the ``view`` query argument:

>>> browser.open(
...     'http://localhost/++skin++cms/@@redirect_to'
...     '?unique_id=http://xml.zeit.de/online/2007/01/Somalia'
...     '&view=@@drag-pane.html')
>>> browser.url
'http://localhost/++skin++cms/repository/online/2007/01/Somalia/@@drag-pane.html'

If no object with the given UID can be found, an ugly but useful error is
returned:

>>> browser.open(
...     'http://localhost/++skin++cms/@@redirect_to'
...     '?unique_id=blafasel')
>>> print(browser.contents)
<div class="error">The object 'blafasel' could not be found.</div>


Invalidating the cache
======================

There is a button in the UI to invalidate the cache, or in other words to
reload. Reloading sends an IResourceInvalidatedEvent.

>>> import zeit.connector.interfaces
>>> @zope.component.adapter(
...     zeit.connector.interfaces.IResourceInvalidatedEvent)
... def invalid(event):
...     print("Invalidate: %s" % event.id)
>>> gsm = zope.component.getGlobalSiteManager()
>>> gsm.registerHandler(invalid)


>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01')
>>> browser.getLink('Reload').click()
Invalidate: http://xml.zeit.de/online/2007/01/
>>> browser.url
'http://localhost/++skin++cms/repository/online/2007/01/@@view.html'


Clean up:

>>> gsm.unregisterHandler(invalid)
True

