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
