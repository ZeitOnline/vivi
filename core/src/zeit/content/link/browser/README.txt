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
>>> browser.open(menu.value[0])

Now we're looking at the add form. Fill in some data:

>>> browser.handleErrors = False
>>> browser.getControl('File name').value = 'gocept.link'
>>> browser.getControl('Title').value = 'gocept homepage'
>>> browser.getControl('Teaser title').value = 'gocept teaser'
>>> browser.getControl('Link address').value = 'http://gocept.com'
>>> browser.getControl(name='form.authors.0.').value = 'Hans Sachs'
>>> browser.getControl(name='form.actions.add').click()

After adding the link is *not* checked out, because there is nothing more to
edit:

>>> browser.url
'http://localhost/++skin++cms/repository/online/2007/01/gocept.link/@@view.html'

We need to add an image, so check out the link:

>>> browser.getLink('Checkout').click()

Add an image:

>>> browser.getControl('Add Images').click()
>>> browser.getControl(name="form.images.0.").value = (
...     'http://xml.zeit.de/2006/DSC00109_2.JPG')
>>> browser.getControl('Apply').click()
>>> 'There were errors' in browser.contents
False


Have a look at the source:

>>> browser.getLink('Source').click()
>>> print browser.getControl(name='form.xml').value
<link>
  <head>
    <image src="http://xml.zeit.de/2006/DSC00109_2.JPG" type="jpeg">
      <bu xmlns:ns0="http://www.w3.org/2001/XMLSchema-instance" ns0:nil="true"/>
      <copyright xmlns:ns1="http://www.w3.org/2001/XMLSchema-instance" ns1:nil="true"/>
    </image>
  </head>
  <body>
    <url>http://gocept.com</url>
    <title>gocept homepage</title>
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


Verify the source of the feed (note that the images are still missing, bug
#3956):

>>> browser.open('http://localhost/++skin++cms/repository/politik.feed')
>>> browser.getLink('Checkout').click()
>>> browser.getLink('Source').click()
>>> print browser.getControl(name='form.xml').value
<feed xmlns="http://namespaces.zeit.de/CMS/feed">
  <title>Politik</title>
  <container>
    <block href="http://xml.zeit.de/online/2007/01/gocept.link">
      <supertitle xmlns:ns1="http://www.w3.org/2001/XMLSchema-instance" ns1:nil="true"/>
      <title>gocept teaser</title>
      <text xmlns:ns2="http://www.w3.org/2001/XMLSchema-instance" ns2:nil="true"/>
      <byline xmlns:ns3="http://www.w3.org/2001/XMLSchema-instance" ns3:nil="true"/>
      <short>
        <title xmlns:ns4="http://www.w3.org/2001/XMLSchema-instance" ns4:nil="true"/>
        <text xmlns:ns5="http://www.w3.org/2001/XMLSchema-instance" ns5:nil="true"/>
      </short>
      <image src="http://xml.zeit.de/2006/DSC00109_2.JPG" type="jpeg">
        <bu xmlns:ns0="http://www.w3.org/2001/XMLSchema-instance" ns0:nil="true"/>
        <copyright xmlns:ns1="http://www.w3.org/2001/XMLSchema-instance" ns1:nil="true"/>
      </image>
    </block>
  </container>
</feed>

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
    <title> View link metadata </title>
    ...

 
