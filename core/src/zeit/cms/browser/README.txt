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
    <title>
           Object: &lt;zope...Folder object at 0x...&gt;, name: u'doesnotexist' – Zeit CMS
    </title>
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


The java script calls `set_folded`:

>>> browser.open(
...     'http://localhost/++skin++cms/@@sidebar_folded?folded=true' )
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
...     'http://localhost/++skin++cms/@@sidebar_folded?folded=false' )
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
     <a class="button" title="Preview" target="_blank"
        href=".../online/2007/01/Somalia/@@show_preview">...
     <a class="button" title="Live" target="_blank"
        href=".../online/2007/01/Somalia/@@show_live">...
     <a title="Development"
        href=".../online/2007/01/Somalia/@@show_development-preview"
        id="..." target="_blank">...


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

Query arguments are passed to the server:

>>> import urllib2
>>> browser.mech_browser.set_handle_redirect(False)
>>> try:
...     browser.open(
...         'http://localhost/++skin++cms/repository/online/2007/01/Somalia/@@show_preview?foo=bar')
... except urllib2.HTTPError, e:
...     print e
...     print e.hdrs.get('location')
... finally:
...    browser.mech_browser.set_handle_redirect(True)
HTTP Error 303: See Other
http://localhost/preview-prefix/online/2007/01/Somalia?foo=bar


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


Drag panes
==========

There is a view which dispatches to the actual drag pane:

>>> browser.open(
...     'http://localhost/++skin++cms/get-drag-pane?'
...     'uniqueId=http://xml.zeit.de/testcontent')
>>> print browser.contents
  <div class="Text">
    :
  </div>
  <div class="UniqueId">http://xml.zeit.de/testcontent</div>
