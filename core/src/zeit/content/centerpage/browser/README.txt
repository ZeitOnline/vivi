============
Center Pages
============

For UI-Tests we need a Testbrowser:

>>> from z3c.etestbrowser.testing import ExtendedTestBrowser
>>> browser = ExtendedTestBrowser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')


Metadata Preview
================

The metadata preview shows the most important data in list views:

>>> browser.open('http://localhost/++skin++cms/repository/online'
...              '/2007/01/index/metadata_preview')
>>> print browser.contents
 <div class="contextViewsAndActions">
    <div class="context-views">...
>>> browser.getLink('Checkout')
<Link text='actionmenuicon[IMG] Checkout' ...>

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
>>> browser.open(menu.value[0])

We are now at the template choose form. Initially there are no templates but
the empty default template:

>>> browser.getControl('Template').displayOptions
['(no value)']

The default template is fine right now, so continue:

>>> browser.getControl('Continue').click()

We are now looking at the add form. Some fields are filled with suitable
defaults:

>>> import datetime
>>> now = datetime.datetime.now()

>>> browser.getControl(name='form.year').value == str(now.year)
True
>>> current_week = str(int(now.strftime('%W')))
>>> if current_week == '0':
...     current_week = '1'
>>> browser.getControl(name='form.volume').value == current_week
True


Now, fill the form and add the CP:

>>> browser.getControl(name='form.year').value = '2007'
>>> browser.getControl(name='form.volume').value = '2'
>>> browser.getControl(name='form.__name__').value = 'index'
>>> browser.getControl(name='form.title').value = 'Politik'
>>> browser.getControl('Ressort').displayValue = ['Deutschland']
>>> browser.getControl(name='form.authors.0.').value = 'Hans Sachs'
>>> browser.getControl(name='form.actions.add').click()


After submitting the object is automatically checked out to the working copy
and we're looking at the metadata screen (i.e. edit form):

>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.user/index/@@edit.html'

>>> browser.getControl(name='form.year').value
'2007'
>>> browser.getControl(name='form.volume').value
'2'
>>> browser.getControl(name='form.title').value
'Politik'


Make sure there is the edit metadata tab:

>>> browser.getLink('Edit metadata').click()
>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.user/index/@@edit.html'


Note that the metadata view screen is not available on checked out center
pages:

>>> browser.getLink('View metadata')
Traceback (most recent call last):
    ...
LinkNotFoundError


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

>>> browser.getLink('Edit content').click()
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
>>> ajax.addHeader('Authorization', 'Basic user:userpw')
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

>>> browser.getLink('Source').click()
>>> print browser.getControl(name='form.xml').value
<centerpage xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="year">2007</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="volume">2</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="ressort">Deutschland</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="author">Hans Sachs</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="copyrights">ZEIT online</attribute>
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
...      <attribute ns="http://namespaces.zeit.de/CMS/document" name="ressort">Deutschland</attribute>
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
>>> 'Premature end of data in tag a line 1, line 1, column 4' in browser.contents
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


Templates
=========

An administrator can edit the center page templates. Log in as admin:

>>> admin = ExtendedTestBrowser()
>>> admin.addHeader('Authorization', 'Basic globalmgr:globalmgrpw')
>>> admin.open('http://localhost:8080/++skin++cms')

Go to the CP template manager:

>>> admin.getLink('Templates').click()
>>> admin.getLink('Centerpage templates').click()
>>> menu = admin.getControl(name='add_menu')
>>> menu.displayValue = ['Template']
>>> admin.open(menu.value[0])
>>> admin.getControl('Title').value = 'Homepagevorlage'
>>> admin.getControl('Source').value = (
...     '<centerpage><head/><body><title>Homepage</title>'
...     '<column layout="left"><container style="r07"/></column>'
...     '</body></centerpage>')
>>> admin.getControl('Add').click()
>>> print admin.contents
<?xml ...
<!DOCTYPE ...
    <title> Edit webdav properties </title>
    ...

>>> admin.getControl(name='namespace:list').value = (
...     'http://namespaces.zeit.de/CMS/document')
>>> admin.getControl(name='name:list').value = 'page'
>>> admin.getControl(name='value:list').value = '27'
>>> admin.getControl('Save').click()


After having added the template, we are ready to use it:

>>> browser.getLink('online').click()
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Center-Page']
>>> browser.open(menu.value[0])
>>> browser.getControl('Template').displayOptions
['(no value)', 'Homepagevorlage']

Select homepage and create the centerpage:

>>> browser.getControl('Template').displayValue = ['Homepagevorlage']
>>> browser.getControl('Continue').click()

Now we're at the add page, title and page are already filled:

>>> browser.getControl('Title').value
'Homepage'
>>> browser.getControl('Page').value
'27'

Set the required fields and add the centerpage:

>>> browser.getControl('File name').value = 'new-home'
>>> browser.getControl('Year').value = '2007'
>>> browser.getControl('Volume').value = '28'
>>> browser.getControl('Ressort').displayValue = ['International']
>>> browser.getControl(name='form.authors.0.').value = 'Hans Sachs'
>>> browser.getControl(name="form.actions.add").click()
>>> 'There were errors' in browser.contents
False


Have a look at the source:

>>> browser.getLink('Source').click()
>>> print browser.getControl('XML Source').value
<centerpage>
  <head>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="year">2007</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="volume">28</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="page">27</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="ressort">International</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="author">Hans Sachs</attribute>
    <attribute xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="copyrights">ZEIT online</attribute>
  </head>
  <body>
    <title>Homepage</title>
    <column layout="left">
      <container style="r07"/>
    </column>
  </body>
</centerpage>
