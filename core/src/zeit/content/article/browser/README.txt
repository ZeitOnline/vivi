==========
Article UI
==========

For UI-Tests we need a Testbrowser:

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')

Metadata Preview
================

The metadata preview shows the most important data in list views:

>>> browser.open('http://localhost:8080/++skin++cms/repository/online'
...              '/2007/01/Somalia/metadata_preview')
>>> print browser.contents
 <div class="contextViewsAndActions">
    <div class="context-views">...
    <div class="context-actions">...
    <div id="metadata_preview">...
      <div class="teaser-title" title="Teaser">...

>>> browser.getLink('Checkout')
<Link text='[IMG] Checkout...>

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
        <span class="filename">Ford-Beerdigung</span>
    </td>
    <td>
      2008 3 7  12:47:16
    </td>
    <td>
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
>>> print url
http://localhost/++skin++cms/repository/online/2007/01/@@zeit.content.article.Add
>>> browser.open(url)

The article is created and checked out automatically. The editor is open:

>>> print browser.title.strip()
e0135811-d21a-4e29-918e-1b0dde4e0c38.tmp – Edit
>>> print browser.url
http://localhost/++skin++cms/workingcopy/zope.user/e0135811-d21a-4e29-918e-1b0dde4e0c38.tmp/@@edit.html


Note that the metadata view screen is not available on checked out articles:

>>> browser.getLink('View metadata')
Traceback (most recent call last):
    ...
LinkNotFoundError


Editing Articles
================

Let's change some data and save the article:

>>> browser.open('@@edit-metadata.html')
>>> browser.getControl(name='form.year').value = '2007'
>>> browser.getControl(name='form.volume').value = '2'
>>> browser.getControl('Ressort').displayValue = ['Deutschland']
>>> browser.getControl(name='form.authors.0.').value = 'Hans Sachs'
>>> browser.getControl('Sub ressort').displayOptions
['(no value)', 'Joschka Fisher', 'Integration', 'Meinung', 'Datenschutz', 'US-Wahl', 'Nahost']
>>> browser.getControl('Sub ressort').displayValue = ['Integration']
>>> browser.getControl('VG Wort Id').value = 'ada94da'
>>> browser.getControl(name='form.title').value = (
...   'EU unterstuetzt Trinker-Steuer')
>>> browser.getControl('Apply').click()
>>> 'There were errors' in browser.contents
False

We get the form back after saving, the data is changed:

>>> browser.getControl(name='form.title').value
'EU unterstuetzt Trinker-Steuer'

It is not possible to change the file name in the edit view:

>>> browser.getControl('File name')
Traceback (most recent call last):
    ...
LookupError: label 'File name'

Relating images and other content is done on the "asset" page. There is no
read-only view to the assets:

>>> browser.getLink('Assets').click()
Traceback (most recent call last):
    ...
LinkNotFoundError

>>> browser.getLink('Edit assets').click()

Let's add an image:

>>> browser.getControl('Add Images').click()
>>> browser.getControl(name="form.images.0.").value = (
...     'http://xml.zeit.de/2006/DSC00109_2.JPG')
>>> browser.getControl('Apply').click()
>>> 'There were errors' in browser.contents
False

Let's relate a content object:

>>> browser.getControl('Add Related content').click()
>>> browser.getControl(name="form.related.0.").value = (
...     'http://xml.zeit.de/online/2007/01/thailand-anschlaege')
>>> browser.getControl('Apply').click()
>>> 'There were errors' in browser.contents
False


We also want to add an image group[2]_.

>>> browser.getControl('Add Images').click()
>>> browser.getControl(name="form.images.1.").value = group.uniqueId

Aggregate the comments of another object:

>>> browser.getControl('Aggregate comments').value = (
...     'http://xml.zeit.de/online/2007/01/Somalia')

Apply changes:

>>> browser.getControl('Apply').click()
>>> print browser.contents
<?xml ...
    ...Updated on...

Verify:

>>> browser.getControl(name="form.images.0.").value
'http://xml.zeit.de/2006/DSC00109_2.JPG'


WYSIWYG-Editor
++++++++++++++

Open the WYSIWYG-Editor:

>>> browser.getLink('Edit WYSIWYG').click()

Some important fields can be edited here as well:

>>> browser.getControl('Kicker').value = 'Halle'
>>> browser.getControl('Title').value
'EU unterstuetzt Trinker-Steuer'
>>> browser.getControl('By line').value = 'by Dr. Who'
>>> browser.getControl('Subtitle').value = 'Bla blub blarf'

Initially the document is empty:

>>> browser.getControl('Text').value
''

Change the content and save:

>>> browser.getControl('Text').value = '<p>Foo</p><h3>blub</h3>'
>>> browser.getControl('Apply').click()

Let's have a look at the source:

>>> browser.getLink('Source').click()
>>> print browser.getControl('Source').value.replace('\r\n', '\n')
<article xmlns:py="http://codespeak.net/lxml/objectify/pytype">
    ...
  <body>
    <title>EU unterstuetzt Trinker-Steuer</title>
    <supertitle py:pytype="str">Halle</supertitle>
    <byline py:pytype="str">by Dr. Who</byline>
    <subtitle>Bla blub blarf</subtitle>
    <division type="page">
      <p>Foo</p>
      <intertitle>blub</intertitle>
    </division>
  </body>
</article>


Try to add some xml characters to the WYSIWYG editor as entities but make sure
other entities will be replaced (this is to make sure bug #3900 is fixed):

>>> browser.getLink('Edit WYSIWYG').click()
>>> browser.getControl('Text').value = (
...     '<p>Foo</p><h3>blub &mdash;</h3><p>&gt;&amp;&lt;</p>')
>>> browser.getControl('Apply').click()
>>> print browser.getControl('Text').value,
<p>Foo</p>
<h3>blub —</h3>
<p>&gt;&amp;&lt;</p>


Empty tags will be removed on saving:

>>> browser.getControl('Text').value = (
...     '<p>Foo</p><h3/><foo/><p/><p><b>bar</b></p>')
>>> browser.getControl('Apply').click()
>>> print browser.getControl('Text').value
<p>Foo</p>
<p>
  <b>bar</b>
</p>


Checking in
===========

We check in the document. We look at the document in the repository then:

>>> browser.getLink('Checkin').click()
>>> article_url = browser.url
>>> article_url
'http://localhost/++skin++cms/repository/.../...tmp/@@view.html'


Let's make sure the image is linked:

>>> browser.getLink('Assets').click()
>>> print browser.contents
<?xml ...
<li>...<a href="http://localhost/++skin++cms/repository/2006/DSC00109_2.JPG"...
<li>...<a href="http://localhost/++skin++cms/repository/image-group"...

After checking in we also do not have an edit metadata link:

>>> browser.getLink('Edit metadata')
Traceback (most recent call last):
    ...
LinkNotFoundError

There was a bug once where after editing an article there were edit fields on
the read only form:

>>> browser.getControl('Teaser text')
Traceback (most recent call last):
    ...
LookupError: label 'Teaser text'


But a view tab is there:

>>> browser.getLink('View metadata').click()
>>> browser.url
'http://localhost/++skin++cms/repository/.../...tmp/@@view.html'


Syndicating
===========

When we syndicate the article the feed will be linked in the article. Let's use
`politik.feed` as a syndication target:

>>> browser.getLink('Syndicate').click()
>>> print browser.contents
<?xml ...
<!DOCTYPE ...
    <p>
    You need to select a feed as a syndication target first, before you
    can syndicate this article.
    </p>
    ...
>>> url = browser.url
>>> browser.open('http://localhost/++skin++cms/repository/politik.feed')
>>> browser.getLink('Remember as syndication target').click()
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
>>> browser.getLink('Source').click()
>>> print browser.getControl(name='form.xml').value.replace('\r\n', '\n')
<channel>
  <title>Politik</title>
  <container>
    <block ...href="http://xml.zeit.de/online/2007/01/...tmp" year="2007" issue="2"...>
      <supertitle py:pytype="str">Halle</supertitle>
      <title xsi:nil="true"/>
      <text xsi:nil="true"/>
      <description xsi:nil="true"/>
      <byline py:pytype="str">by Dr. Who</byline>
      <image src="http://xml.zeit.de/2006/DSC00109_2.JPG" type="JPG"...>
        <bu xsi:nil="true"/>
        <copyright...
      </image>
    </block>
  </container>
  <object_limit xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="int">50</object_limit>
</channel>
>>> browser.getLink('Checkin').click()


Checking in a Syndicated Article
================================

We change the article's teaser and check it in. We expect to see the change in
the feeds automatically:

>>> browser.open(article_url)
>>> browser.getLink('Checkout').click()
>>> browser.getLink('Edit metadata').click()
>>> browser.getControl(name='form.teaserTitle').value = 'Trinker zur Kasse'
>>> browser.getControl('Apply').click()
>>> browser.getLink('Checkin').click()
>>> import gocept.async.tests
>>> import zope.app.component.hooks
>>> old_site = zope.app.component.hooks.getSite()
>>> zope.app.component.hooks.setSite(getRootFolder())
>>> gocept.async.tests.process('events')
>>> zope.app.component.hooks.setSite(old_site)

Now the feed has been changed. Verify this by checking out the feed and looking
at its xml source:

>>> browser.open('http://localhost/++skin++cms/repository/politik.feed')
>>> browser.getLink('Checkout').click()
>>> browser.getLink('Source').click()
>>> print browser.getControl(name='form.xml').value.replace('\r', '')
<channel>
  <title>Politik</title>
  <container>
    <block ...href="http://xml.zeit.de/online/2007/01/...tmp" year="2007" issue="2"...>
      <supertitle py:pytype="str">Halle</supertitle>
      <title py:pytype="str">Trinker zur Kasse</title>
      <text xsi:nil="true"/>
      <description xsi:nil="true"/>
      <byline py:pytype="str">by Dr. Who</byline>
      <image src="http://xml.zeit.de/2006/DSC00109_2.JPG" type="JPG"...>
        <bu xsi:nil="true"/>
        <copyright...
      </image>
    </block>
  </container>
  <object_limit xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="int">50</object_limit>
</channel>

Check the feed back in to have nothing laying around:

>>> browser.getLink('Checkin').click()


.. [2] Create an image group. To create it we need to setup the site:

    >>> import zope.app.component.hooks
    >>> old_site = zope.app.component.hooks.getSite()
    >>> zope.app.component.hooks.setSite(getRootFolder())

    Create the group:

    >>> import zeit.content.image.tests
    >>> group = zeit.content.image.tests.create_image_group()

    Commit the transaction so our browser sees the change. Also unset the site
    again:

    >>> import transaction
    >>> transaction.commit()
    >>> zope.app.component.hooks.setSite(old_site)
