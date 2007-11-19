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
