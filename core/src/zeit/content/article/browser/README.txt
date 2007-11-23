==========
Article UI
==========

For UI-Tests we need a Testbrowser:

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')

Metadata Preview
================

The metadata preview shows the most important data in list views:

>>> browser.open('http://localhost:8080/++skin++cms/repository/online'
...              '/2007/01/Somalia/metadata_preview')
>>> print browser.contents
<BLANKLINE>
  <div class="heading">
     ...
    <h2>...
    <div class="context-views">...
    <div id="metadata_preview">...
      <div class="teaser-title" title="Teaser">...

>>> browser.getLink('Checkout')
<Link text='Checkout' ...>

Make sure we have a "view" link:
>>> browser.getLink('View')
<Link text='View' ...>


We have to publish another url to see if articles are listed:

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01')
>>> print browser.contents
<?xml version...
<!DOCTYPE ...
...
    <td> 
      <img...IArticle-zmi_icon.png...
    </td>
    <td>
      Ford wird beigesetzt
    </td>
    <td>
      1
    </td>
    <td>
      2007
    </td>
    <td>
      International
    </td>
...


Creating Articles
=================

Articles can be created through the add menu in the repository. We open an
arbitrary url and add an article then:

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Article']
>>> url = menu.value[0]
>>> url
'http://localhost/++skin++cms/repository/online/2007/01/@@zeit.content.article.Add'
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


Now, fill the form and add the article:

>>> browser.getControl(name='form.year').value = '2007'
>>> browser.getControl(name='form.volume').value = '2'
>>> browser.getControl(name='form.__name__').value = 'KFZ-Steuer'
>>> browser.getControl(name='form.title').value = (
...     'EU unterstuetzt Stinker-Steuer')
>>> browser.getControl(name='form.actions.add').click()
>>> 'There were errors' in browser.contents
False

After submitting we're looking at the object in our working copy. The Metadata
edit screen should be displayed:

>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.mgr/KFZ-Steuer/@@edit.html'

>>> browser.getControl(name='form.year').value
'2007'
>>> browser.getControl(name='form.volume').value
'2'
>>> browser.getControl(name='form.title').value
'EU unterstuetzt Stinker-Steuer'


Editing Articles
================


Let's change some data and save the article:

>>> browser.getControl(name='form.title').value = (
...   'EU unterstuetzt Trinker-Steuer')
>>> browser.getControl('Apply').click()

We get the form back after saving, the data is changed:

>>> browser.getControl(name='form.title').value
'EU unterstuetzt Trinker-Steuer'


Checking in 
===========

We check in the document. We look a the document in the repository then:

>>> browser.getLink('Checkin').click()
>>> article_url = browser.url
>>> article_url
'http://localhost/++skin++cms/repository/.../KFZ-Steuer/@@view.html'
 

Syndicating
===========

When we syndicate the article the feed will be linked in the article. Let's use
`politik.feed` as a syndication target:

>>> url = browser.url
>>> browser.open('http://localhost/++skin++cms/repository/politik.feed')
>>> browser.getLink('Als Ziel merken').click()
>>> browser.open(url)

>>> browser.getLink('Syndicate').click()
>>> checkbox = browser.getControl(
...    name='selection_column.aHR0cDovL3htbC56ZWl0LmRlL3BvbGl0aWsuZmVlZA==.')
>>> checkbox.value = True
>>> browser.getControl('Syndicate').click()

The article is now syndicated in the feed. Verify this by looking at the feed
xml source:

>>> browser.open('http://localhost/++skin++cms/repository/politik.feed')
>>> browser.getLink('Checkout').click()
>>> browser.getLink('Quelltext').click()
>>> print browser.getControl(name='form.xml').value
<feed xmlns="http://namespaces.zeit.de/CMS/feed">
  <title>Politik</title>
  <container>
    <block href="http://xml.zeit.de/online/2007/01/KFZ-Steuer">
      <teaser xmlns="http://xml.zeit.de/CMS/Teaser">
        <title/>
        <text/>
      </teaser>
      <indexteaser xmlns="http://xml.zeit.de/CMS/Teaser">
        <title/>
        <text/>
      </indexteaser>
    </block>
  </container>
</feed>
>>> browser.getLink('Checkin').click()


Let's make sure the feed is referenced in the article:

>>> browser.open(article_url)
>>> browser.getLink('Checkout').click()
>>> browser.getLink('Quelltext').click()
>>> print browser.getControl(name='form.xml').value
<article...
  <attribute
    ns="http://namespaces.zeit.de/CMS/document"
    name="syndicatedIn">http://xml.zeit.de/politik.feed</attribute>
...
</article>


Checking in a Syndicated Article
================================

We change the article's teaser and check it in. We expect to see the change in
the feeds automatically:

>>> browser.getLink('Metadaten').click()
>>> browser.getControl(name='form.teaserTitle').value = 'Trinker zur Kasse'
>>> browser.getControl('Apply').click()
>>> browser.getLink('Checkin').click()
>>> browser.open('http://localhost/++skin++cms/repository/politik.feed')
>>> browser.getLink('Checkout').click()
>>> browser.getLink('Quelltext').click()
>>> print browser.getControl(name='form.xml').value
<feed xmlns="http://namespaces.zeit.de/CMS/feed">
  <title>Politik</title>
  <container>
    <block href="http://xml.zeit.de/online/2007/01/KFZ-Steuer">
      <teaser xmlns="http://xml.zeit.de/CMS/Teaser">
        <title>Trinker zur Kasse</title>
        <text/>
      </teaser>
      <indexteaser xmlns="http://xml.zeit.de/CMS/Teaser">
        <title/>
        <text/>
      </indexteaser>
    </block>
  </container>
</feed>

>>> browser.getLink('Checkin').click()
