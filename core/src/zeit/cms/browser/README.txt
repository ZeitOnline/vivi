=======================
ZEIT CMS User Interface
=======================


Anonymous Access
================

Anonymous access to the CMS is *not* possible:

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.open('http://localhost/++skin++cms/')
Traceback (most recent call last):
  ...
HTTPError: HTTP Error 401: Unauthorized

With credentials we don't get an error:

>>> browser.addHeader('Authorization', 'Basic user:userpw')
>>> browser.open('http://localhost/++skin++cms/')

Not Found
=========

Make sure we have a decent 404 page:

>>> browser.open('http://localhost/++skin++cms/doesnotexist')
Traceback (most recent call last):
    ...
HTTPError: HTTP Error 404: Not Found

>>> print browser.contents
<?xml ...
    <title> Zeit CMS </title>
    ...


Sidebar Folding
===============

The sidebar remembers its folding state. This is dependent on the user.

Initially the sidebar is open (expanded):

>>> browser.open('http://localhost/++skin++cms/' )
>>> print browser.contents
<?xml ...
<!DOCTYPE ...
    <div id="sidebar" class="sidebar-expanded">...
    <div id="sidebar-dragger" class="sidebar-expanded">...
    <div id="visualContentWrapper" class="sidebar-expanded">...


The java script calls `toggle_folding` which will toggle the folding:

>>> browser.open(
...     'http://localhost/++skin++cms/@@sidebar_toggle_folding' )
>>> browser.contents
'sidebar-folded'

So with the next page load the panel is folded:

>>> browser.open('http://localhost/++skin++cms/' )
>>> print browser.contents
<?xml ...
<!DOCTYPE ...
    <div id="sidebar" class="sidebar-folded">...
    <div id="sidebar-dragger" class="sidebar-folded">...
    <div id="visualContentWrapper" class="sidebar-folded">...


Toggling again will expand the sidebar again:

>>> browser.open(
...     'http://localhost/++skin++cms/@@sidebar_toggle_folding' )
>>> browser.contents
'sidebar-expanded'
>>> browser.open('http://localhost/++skin++cms/' )
>>> print browser.contents
<?xml ...
<!DOCTYPE ...
    <div id="sidebar" class="sidebar-expanded">...
    <div id="sidebar-dragger" class="sidebar-expanded">...
    <div id="visualContentWrapper" class="sidebar-expanded">...


Preview
=======

There are three preview or live view links. The "preview" shows the document as
it is stored in the repository with the current live templates. The live
preview shows the version on zeit.de and the development preview can be used
for trying out new templates. The preview actions are only shown on repository
content.


Make sure the menu entries are there and the targets are _blank:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/Somalia' )
>>> print browser.contents
<?xml ...
    <li class="preview ">
     <a href=".../online/2007/01/Somalia/@@show_preview" target="_blank"
        title="Preview">...
   </li>
   <li class="live ">
     <a href=".../online/2007/01/Somalia/@@show_live" target="_blank"
        title="Live">...
   </li>
   <li class="development ">
     <a href=".../online/2007/01/Somalia/@@show_development-preview"
        target="_blank" title="Development">...
   </li>
   ...


Check the preview:

>>> import zeit.cms.testing
>>> zeit.cms.testing.click_wo_redirect(browser, 'Preview')
HTTP Error 303: See Other
http://localhost/preview-prefix/online/2007/01/Somalia


Check the live site:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/Somalia' )
>>> zeit.cms.testing.click_wo_redirect(browser, 'Live')
HTTP Error 303: See Other
http://localhost/live-prefix/online/2007/01/Somalia


Check the development preview:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/Somalia' )
>>> zeit.cms.testing.click_wo_redirect(browser, 'Development')
HTTP Error 303: See Other
http://localhost/development-preview-prefix/online/2007/01/Somalia

When an adapter to IPreviewObject is registered the preview url may change.
Register an adapter for IUnknownResource redirecting to the container:

>>> import zope.component
>>> import zeit.cms.browser.interfaces
>>> import zeit.cms.repository.interfaces
>>> def preview(context):
...     return context.__parent__
>>> gsm = zope.component.getGlobalSiteManager()
>>> gsm.registerAdapter(
...     preview,
...     (zeit.cms.repository.interfaces.IUnknownResource, ),
...     zeit.cms.browser.interfaces.IPreviewObject)

The preview is on the container now:


>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/Somalia' )
>>> zeit.cms.testing.click_wo_redirect(browser, 'Development')
HTTP Error 303: See Other
http://localhost/development-preview-prefix/online/2007/01


Clean up:
>>> gsm.unregisterAdapter(
...     preview,
...     (zeit.cms.repository.interfaces.IUnknownResource, ),
...     zeit.cms.browser.interfaces.IPreviewObject)
True
