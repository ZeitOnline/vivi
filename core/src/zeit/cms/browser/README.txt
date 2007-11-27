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


Sidebar Folding
===============

The sidebar remembers its folding state. This is dependent on the user, so
let's log in one:

>>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')

Initially the sidebar is open (expanded):

>>> browser.open('http://localhost/++skin++cms/' )
>>> print browser.contents
<?xml ...
<!DOCTYPE ...
    <div id="sidebar" class="sidebar-expanded">...
    <div id="sidebar-dragger" class="sidebar-expanded">...
    <div id="content" class="sidebar-expanded">...


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
    <div id="content" class="sidebar-folded">...


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
    <div id="content" class="sidebar-expanded">...


Preview
=======

There are three preview or live view links. The "preview" shows the document as
it is stored in the repository with the current live templates. The live
preview shows the version on zeit.de and the development preview can be used
for trying out new templates. The preview actions are only shown on repository
content.


Make sure the menu entries are there:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/Somalia' )
>>> print browser.contents
<?xml ...
    <li class="Preview">
     <a href=".../online/2007/01/Somalia/@@show_preview">Preview</a>
   </li>
   <li class="Live">
     <a href=".../online/2007/01/Somalia/@@show_live">Live</a>
   </li>
   <li class="Development">
     <a href=".../online/2007/01/Somalia/@@show_development-preview">Development</a>
   </li>
   ...


For testing the redirect we need a little helper:

>>> def click_wo_redirect(*args, **kwargs):
...     import urllib2
...     browser.mech_browser.set_handle_redirect(False)
...     try:
...         try:
...             browser.getLink(*args, **kwargs).click()
...         except urllib2.HTTPError, e:
...             print str(e)
...             print e.headers.get('location')
...     finally:
...         browser.mech_browser.set_handle_redirect(True)


Check the preview:

>>> click_wo_redirect('Preview')
HTTP Error 303: See Other
http://localhost/preview-prefix/online/2007/01/Somalia


Check the live site:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/Somalia' )
>>> click_wo_redirect('Live')
HTTP Error 303: See Other
http://localhost/live-prefix/online/2007/01/Somalia


Check the development preview:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/Somalia' )
>>> click_wo_redirect('Development')
HTTP Error 303: See Other
http://localhost/development-preview-prefix/online/2007/01/Somalia
