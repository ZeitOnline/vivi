============
Center Pages
============

For UI-Tests we need a Testbrowser:

>>> from z3c.etestbrowser.testing import ExtendedTestBrowser
>>> browser = ExtendedTestBrowser()
>>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')


Metadata Preview
================

The metadata preview shows the most important data in list views:

>>> browser.open('http://localhost/++skin++cms/repository/online'
...              '/2007/01/index/metadata_preview')
>>> print browser.contents
    <div class="context-views">...
>>> browser.getLink('Checkout')
<Link text='[IMG] Checkout' ...>

We have to publish another url to see if articles are listed:

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01')
>>> len(browser.etree.xpath("//table[contains(@class, 'contentListing')]/tbody/tr"))
53

Creating Center Pages
=====================

CPs can be created through the add menu in the repository. We open an arbitrary
url and add a CP then:

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/02')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Center-Page']
>>> url = menu.value[0]
>>> url
'http://localhost/++skin++cms/repository/online/2007/02/@@zeit.content.centerpage.Add'
>>> browser.open(menu.value[0])

We are now looking at the add form. Some fields are filled with suitable
defaults:

>>> import datetime
>>> now = datetime.datetime.now()

>>> browser.getControl(name='form.year').value == str(now.year)
True
>>> browser.getControl(name='form.volume').value == str(int(
...     now.strftime('%W')))
True


Now, fill the form and add the CP:

>>> browser.getControl(name='form.year').value = '2007'
>>> browser.getControl(name='form.volume').value = '2'
>>> browser.getControl(name='form.__name__').value = 'index'
>>> browser.getControl(name='form.title').value = 'Politik'
>>> browser.getControl('Ressort').value
'Online'
>>> browser.handleErrors = False
>>> browser.getControl(name='form.actions.add').click()


After submitting the object is automatically checked out to the working copy
and we're looking at the metadata screen (i.e. edit form):

>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.mgr/index/@@edit.html'

>>> browser.getControl(name='form.year').value
'2007'
>>> browser.getControl(name='form.volume').value
'2'
>>> browser.getControl(name='form.title').value
'Politik'


Make sure there is the edit metadata tab:

>>> browser.getLink('Edit metadata').click()
>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.mgr/index/@@edit.html'


Editing CPs
===========


We change some values and submit:

>>> browser.getControl(name='form.title').value = 'Wirtschaft'
>>> browser.getControl('Apply').click()

We get the value back:

>>> browser.getControl(name='form.title').value
'Wirtschaft'


XML-Editor
==========

Let's open up the XML editor:

>>> browser.getLink('Bearbeiten').click()
>>> print browser.contents
<?xml ...
<!DOCTYPE ...
  <div id="xml-editor" ...


We cannot really test a lot here as the editor relies heavily on JavaScript.
But we can fake some requests to the server and see it behaves as expected. Get
the `path` of the body element:

>>> body = browser.etree.xpath('//*[@xml-tag-name="body"]')[0]
>>> path = body.get('path')

With another browser, we do the "ajax" requests:

>>> import urllib
>>> ajax = ExtendedTestBrowser()
>>> ajax.addHeader('Authorization', 'Basic mgr:mgrpw')
>>> ajax.open('%s/addChildView?action=append-child&path=%s' % (
...       browser.url, urllib.quote(path)))
>>> print ajax.contents
  <h1>Knoten hinzufügen</h1>
  <ul>
    <li action="append-child" xml-tag="column">column</li>
    <li action="append-child" xml-tag="row">row</li>
    <li action="append-child"
        xml-tag="{http://www.w3.org/2001/XInclude}include">xi:include</li>
  </ul>

We now actually add an element, a column:

>>> ajax.open('%s/appendChild?action=append-child&path=%s&tag=column' % (
...       browser.url, urllib.quote(path)))

>>> import cjson
>>> data = cjson.decode(ajax.contents)
>>> print data['value']['xml']
<div xmlns:zeit="http://www.zeit.de/exslt"
     xmlns:editor="http://www.zeit.de/xml-editor"
    xmlns:xi="http://www.w3.org/2001/XInclude"
    path="/*[1]/*[2]" id="..."
    xml-tag-name="body">
    ...
  <div path="/*[1]/*[2]..." id="..." xml-tag-name="column">
    <div class="block-meta">
        Layout:
    </div>
  </div>
</div>



Source Editor
=============

With the source editor you can just edit the plain source  code of a center
page:

>>> browser.getLink('Quelltext').click()
>>> print browser.getControl(name='form.xml').value
<centerpage>
  <head>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="year">2007</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="volume">2</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="ressort">Online</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="copyrights">ZEIT online</attribute>
  </head>
  <body>
    <title>Wirtschaft</title>
    <column/>
  </body>
</centerpage>


Let's change the source of the center page:

>>> new_cp = '''
...  <centerpage>
...    <head>
...      <attribute ns="http://namespaces.zeit.de/CMS/document" name="ressort">Online</attribute>
...      <attribute ns="http://namespaces.zeit.de/CMS/document" name="volume">2</attribute>
...      <attribute ns="http://namespaces.zeit.de/CMS/document" name="year">2007</attribute>
...      <attribute ns="http://namespaces.zeit.de/CMS/document" name="copyrights">ZEIT online</attribute>
...      <attribute ns="http://namespaces.zeit.de/CMS/document" name="serie"></attribute>
...    </head>
...    <body>
...      <subtitle>In der Wirtschaft gibt's Bier</subtitle>
...      <title>Wirtschaft</title>
...      <column/>
...    </body>
...  </centerpage>
...  '''

When we add an <?xml ...?> header *with* encoding we expect a validation error:

>>> browser.getControl(name='form.xml').value = (
...     '<?xml version="1.0" encoding="latin1" ?>\n%s' % new_cp)
>>> browser.getControl(name='form.actions.apply').click()
>>> 'There were errors' in browser.contents
True
>>> 'Unicode strings with encoding declaration are not supported.' in (
...     browser.contents)
True


Also, when the XML is invalid the validation fails:

>>> browser.getControl(name='form.xml').value = '<a>'
>>> browser.getControl(name='form.actions.apply').click()
>>> 'There were errors' in browser.contents
True
>>> 'line 1: Premature end of data in tag a line 1' in browser.contents
True


Checking in 
===========

We check in the document. We look a the document in the repository then:

>>> browser.getLink('Checkin').click()
>>> browser.url
'http://localhost/++skin++cms/repository/online/2007/02/index/@@view.html'

Make sure there is also a link to the view:

>>> browser.getLink('View metadata').click()
>>> browser.url
'http://localhost/++skin++cms/repository/online/2007/02/index/@@view.html'
