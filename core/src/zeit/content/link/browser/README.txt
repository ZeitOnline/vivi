============
Link objects
============

For UI-Tests we need a Testbrowser:

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')


Creating and editing links
==========================

Create a link object:

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Link']
>>> browser.handleErrors = False
>>> browser.open(menu.value[0])

Now we're looking at the add form. Fill in some data:

>>> browser.getControl('File name').value = 'gocept.link'
>>> browser.getControl('Title').value = 'gocept homepage'
>>> browser.getControl('Ressort').displayValue = ['Leben']
>>> browser.getControl('Teaser title').value = 'gocept teaser'
>>> browser.getControl('Link address').value = 'http://gocept.com'
>>> browser.getControl(name='form.authors.0.').value = 'Hans Sachs'
>>> browser.getControl('Target').displayOptions
['(nothing selected)', 'New window']
>>> browser.getControl(name='form.actions.add').click()

After adding the link is checked out.

>>> 'There were errors' in browser.contents
False

Adding related objects is done on the asset page:

>>> browser.getLink('Edit assets').click()
>>> browser.getControl(name="form.image").value = (
...     'http://xml.zeit.de/2006/DSC00109_2.JPG')
>>> browser.getControl('Add Related').click()
>>> browser.getControl(name="form.related.0.").value = (
...     'http://xml.zeit.de/online/2007/01/Somalia')
>>> browser.getControl('Apply').click()
>>> 'There were errors' in browser.contents
False


Have a look at the source:

>>> browser.getLink('Source').click()
>>> print browser.getControl(name='form.xml').value,
<link xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head>
    <attribute ...
    <references>
      <reference ...type="intern" href="http://xml.zeit.de/online/2007/01/Somalia".../>
    </references>
    <image ...src="http://xml.zeit.de/2006/DSC00109_2.JPG" type="JPG"...>
      <bu xsi:nil="true"/>
      <copyright...
    </image>
  </head>
  <body>
    <title>gocept homepage</title>
    <url>http://gocept.com</url>
  </body>
  <teaser>
    <title>gocept teaser</title>
  </teaser>
</link>


Go back to the edit form:

>>> browser.getLink('Edit metadata').click()


There is no read only view:

>>> browser.getLink('View metadata')
Traceback (most recent call last):
    ...
LinkNotFoundError


Check the link back in:

>>> browser.getLink('Checkin').click()

Now we have the view tab:

>>> browser.getLink('View metadata').click()

Syndicating links
=================

The interesting thing about links is the ability to syndicate them. Let's add a
feed to our syndication list:

>>> bookmark = browser.url
>>> browser.open('http://localhost/++skin++cms/repository/politik.feed')
>>> browser.getLink('Remember as syndication target').click()
>>> browser.open(bookmark)

Syndicate to the politik.feed:

>>> browser.getLink('Syndicate').click()
>>> checkbox = browser.getControl(
...    name='selection_column.aHR0cDovL3htbC56ZWl0LmRlL3BvbGl0aWsuZmVlZA==.')
>>> checkbox.value = True
>>> browser.getControl('Syndicate').click()


Verify the source of the feed:

>>> browser.open('http://localhost/++skin++cms/repository/politik.feed')
>>> browser.getLink('Checkout').click()
>>> browser.getLink('Source').click()
>>> print browser.getControl(name='form.xml').value.replace('\r\n', '\n')
<channel>
  <title>Politik</title>
  <container>
    <block ...
      xmlns:ns0="http://namespaces.zeit.de/CMS/link"
      href="http://xml.zeit.de/online/2007/01/gocept.link"...
      year="2008" issue="26"...
      ns0:href="http://gocept.com"...>
      <supertitle xsi:nil="true"/>
      <title py:pytype="str">gocept teaser</title>
      <text xsi:nil="true"/>
      <description xsi:nil="true"/>
      <byline xsi:nil="true"/>...
      <image src="http://xml.zeit.de/2006/DSC00109_2.JPG" type="JPG"...>
        <bu xsi:nil="true"/>
        <copyright...
      </image>
    </block>
  </container>
  <object_limit xmlns:py="http://codespeak.net/lxml/objectify/pytype">50</object_limit>
</channel>

Check the feed back in to clean up:

>>> browser.getLink('Checkin').click()



Listing
=======

Make sure the links are listed in the directory listings:

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01')
>>> 'gocept homepage' in browser.contents
True


Metadata preview
================

The metadata preview contains the teaser title and the url:

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01/'
...              'gocept.link/@@metadata_preview')
>>> print browser.contents
 <div class="contextViewsAndActions">
    <div class="context-views">
    ...
    <div class="teaser-title" title="Teaser">gocept teaser</div>
    <div class="link-url">
      <a href="http://gocept.com">http://gocept.com</a>
    </div>
    ...


Open the link's metadata view:

>>> browser.getLink('View metadata').click()
>>> print browser.contents
<?xml ...
    <title> gocept homepage – View link metadata </title>
    ...

 
