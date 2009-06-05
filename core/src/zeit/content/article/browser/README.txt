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
<Link text='View metadata' ...>


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
>>> url
'http://localhost/++skin++cms/repository/online/2007/01/@@zeit.content.article.ChooseTemplate'
>>> browser.open(menu.value[0])

We now need to choose a template. Since we haven't created one there is only
the (no value) to be choosen.

>>> browser.getControl('Template').displayOptions
['(no value)']
>>> browser.getControl('Template').displayValue
['(no value)']
>>> browser.getControl('Continue').click()

We are now looking at the add form. Some fields are filled with suitable
defaults:

>>> print browser.contents
<?xml ...
<!DOCTYPE ...
    <title> 01 – Add article </title>
    ...

>>> import datetime
>>> now = datetime.datetime.now()

>>> browser.getControl(name='form.year').value
'2008'
>>> browser.getControl(name='form.volume').value
'26'


Now, fill the form and add the article:

>>> browser.getControl(name='form.year').value = '2007'
>>> browser.getControl(name='form.volume').value = '2'
>>> browser.getControl(name='form.__name__').value = 'KFZ-Steuer'
>>> browser.getControl(name='form.title').value = (
...     'EU <em>unterstuetzt</em> Stinker-Steuer')
>>> browser.getControl('Ressort').displayValue = ['Deutschland']
>>> browser.getControl(name='form.authors.0.').value = 'Hans Sachs'
>>> browser.getControl(name='form.actions.add').click()
>>> browser.getControl('Sub ressort').displayOptions
['(no value)', 'Joschka Fisher', 'Integration', 'Meinung', 'Datenschutz', 'US-Wahl', 'Nahost']
>>> browser.getControl('Sub ressort').displayValue = ['Integration']
>>> browser.getControl('VG Wort Id').value = 'ada94da'
>>> 'There were errors' in browser.contents
False

After submitting we're looking at the object in our working copy. The metadata
edit screen should be displayed:

>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.user/KFZ-Steuer/@@edit.html'
>>> print browser.contents
<?xml ...
<!DOCTYPE ...
    <title>
       EU &lt;em&gt;unterstuetzt&lt;/em&gt; Stinker-Steuer – Edit article
   </title>
    ...

>>> browser.getControl(name='form.year').value
'2007'
>>> browser.getControl(name='form.volume').value
'2'
>>> browser.getControl(name='form.title').value
'EU <em>unterstuetzt</em> Stinker-Steuer'

Note that the metadata view screen is not available on checked out articles:

>>> browser.getLink('View metadata')
Traceback (most recent call last):
    ...
LinkNotFoundError


Editing Articles
================

Let's change some data and save the article:

>>> browser.getControl(name='form.title').value = (
...   'EU unterstuetzt Trinker-Steuer')
>>> browser.getControl('Apply').click()

We get the form back after saving, the data is changed:

>>> browser.getControl(name='form.title').value
'EU unterstuetzt Trinker-Steuer'

It is not possible to change the file name in the edit view:

>>> browser.getControl('File name')
Traceback (most recent call last):
    ...
LookupError: label 'File name'


The article isn't syndicated in any feed for now. The form shouldn't
have a readonly field for Automatic Teasersyndication:

>>> browser.getControl(name="form.automaticTeaserSyndication:list")
Traceback (most recent call last):
    ...
LookupError: name 'form.automaticTeaserSyndication:list'

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


Associate an infobox[1]_:

>>> browser.getControl('Infobox').value = 'http://xml.zeit.de/infobox'


We also want to add an image group[2]_.

>>> browser.getControl('Add Images').click()
>>> browser.getControl(name="form.images.1.").value = group.uniqueId

Also associate a gallery[3]_:

>>> browser.getControl('Image gallery').value = gallery.uniqueId

Also associate a portraitbox[#portraitbox]_:

>>> browser.getControl('Portraitbox').value = 'http://xml.zeit.de/pb'

Aggregate the comments of another object:

>>> browser.getControl('Aggregate comments').value = (
...     'http://xml.zeit.de/online/2007/01/Somalia')

Apply changes:

>>> browser.getControl('Apply').click()
>>> print browser.contents
<?xml ...
    ...Updated on...

Verify some values:

>>> browser.getControl('Infobox').value
'http://xml.zeit.de/infobox'
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
    <p>Foo</p>
    <intertitle>blub</intertitle>
  </body>
</article>


Try to add some xml characters to the WYSIWYG editor as entities but make sure
other entities will be replaced (this is to make sure bug #3900 is fixed):

>>> browser.getLink('Edit WYSIWYG').click()
>>> browser.getControl('Text').value = (
...     '<p>Foo</p><h3>blub &mdash;</h3><p>&gt;&amp;&lt;</p>')
>>> browser.getControl('Apply').click()
>>> browser.getControl('Text').value
'  <p>Foo</p>\r\n  <h3>blub \xe2\x80\x94</h3>\r\n  <p>&gt;&amp;&lt;</p>'


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
'http://localhost/++skin++cms/repository/.../KFZ-Steuer/@@view.html'


Let's make sure the image is linked:

>>> browser.getLink('Assets').click()
>>> print browser.contents
<?xml ...
<li><a href="http://localhost/++skin++cms/repository/2006/DSC00109_2.JPG"...>http://xml.zeit.de/2006/DSC00109_2.JPG</a>...
<li><a href="http://localhost/++skin++cms/repository/image-group"...>http://xml.zeit.de/image-group</a>...

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
'http://localhost/++skin++cms/repository/.../KFZ-Steuer/@@view.html'


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
    <block ...href="http://xml.zeit.de/online/2007/01/KFZ-Steuer" year="2007" issue="2"...>
      <supertitle py:pytype="str">Halle</supertitle>
      <title xsi:nil="true"/>
      <text xsi:nil="true"/>
      <description xsi:nil="true"/>
      <byline py:pytype="str">by Dr. Who</byline>
      <short>
        <title xsi:nil="true"/>
        <text xsi:nil="true"/>
      </short>
      <homepage>
        <title xsi:nil="true"/>
        <text xsi:nil="true"/>
      </homepage>
      <references>
        <reference type="intern" href="http://xml.zeit.de/online/2007/01/thailand-anschlaege" year="2007" issue="1">
          <supertitle py:pytype="str">Thailand</supertitle>
          <title py:pytype="str">Bomben in Bangkok</title>
          <text py:pytype="str">Nach den Anschlägen in Thailand gibt es bislang nur Spekulationen über die Täter. Eines jedoch steht fest: Die Regierung wirkt hilflos. Ein Kommentar</text>
          <description py:pytype="str">Nach den Anschlägen in Thailand gibt es bislang nur Spekulationen über die Täter. Eines jedoch steht fest: Die Regierung wirkt hilflos. Ein Kommentar</description>
          <byline py:pytype="str">von Ulrich Ladurner</byline>
          <short>
            <title py:pytype="str">Thailand</title>
            <text py:pytype="str">Nach den Anschlägen wirkt die Regierung hilflos</text>
          </short>
          <homepage>
            <title xsi:nil="true"/>
            <text xsi:nil="true"/>
          </homepage>
        </reference>
      </references>
      <image src="http://xml.zeit.de/2006/DSC00109_2.JPG" type="JPG">
        <bu xsi:nil="true"/>
        <copyright...
      </image>
    </block>
  </container>
  <object_limit xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="int">50</object_limit>
</channel>
>>> browser.getLink('Checkin').click()

We could now select do not automatically update the metadata:

>>> browser.open(article_url)
>>> browser.getLink('Checkout').click()
>>> browser.getLink('Edit metadata').click()
>>> browser.getControl('No automatic metadata update').displayOptions
['Politik']


Checking in a Syndicated Article
================================

We change the article's teaser and check it in. We expect to see the change in
the feeds automatically:

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
    <block ...href="http://xml.zeit.de/online/2007/01/KFZ-Steuer" year="2007" issue="2"...>
      <supertitle py:pytype="str">Halle</supertitle>
      <title py:pytype="str">Trinker zur Kasse</title>
      <text xsi:nil="true"/>
      <description xsi:nil="true"/>
      <byline py:pytype="str">by Dr. Who</byline>
      <short>
        <title xsi:nil="true"/>
        <text xsi:nil="true"/>
      </short>
      <homepage>
        <title xsi:nil="true"/>
        <text xsi:nil="true"/>
      </homepage>
      <references>
        <reference type="intern" href="http://xml.zeit.de/online/2007/01/thailand-anschlaege" year="2007" issue="1">
          <supertitle py:pytype="str">Thailand</supertitle>
          <title py:pytype="str">Bomben in Bangkok</title>
          <text py:pytype="str">Nach den Anschlägen in Thailand gibt es bislang nur Spekulationen über die Täter. Eines jedoch steht fest: Die Regierung wirkt hilflos. Ein Kommentar</text>
          <description py:pytype="str">Nach den Anschlägen in Thailand gibt es bislang nur Spekulationen über die Täter. Eines jedoch steht fest: Die Regierung wirkt hilflos. Ein Kommentar</description>
          <byline py:pytype="str">von Ulrich Ladurner</byline>
          <short>
            <title py:pytype="str">Thailand</title>
            <text py:pytype="str">Nach den Anschlägen wirkt die Regierung hilflos</text>
          </short>
          <homepage>
            <title xsi:nil="true"/>
            <text xsi:nil="true"/>
          </homepage>
        </reference>
      </references>
      <image src="http://xml.zeit.de/2006/DSC00109_2.JPG" type="JPG">
        <bu xsi:nil="true"/>
        <copyright...
      </image>
    </block>
  </container>
  <object_limit xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="int">50</object_limit>
</channel>

Check the feed back in to have nothing laying around:

>>> browser.getLink('Checkin').click()


Templates
=========

A template can be choosen upon creation of an article. Initially there are no
templates. Creating articles w/o template works as well since there is a
standard template.

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Article']
>>> browser.open(menu.value[0])

The choice allows selecting a "None" value:
>>> browser.getControl('Template').displayOptions
['(no value)']


Let's create two templates. This works via the template manager:


>>> admin = Browser()
>>> admin.addHeader('Authorization', 'Basic globalmgr:globalmgrpw')
>>> admin.open('http://localhost:8080/++skin++cms')
>>> admin.getLink('Templates').click()
>>> admin.getLink('Article templates').click()
>>> menu = admin.getControl(name='add_menu')
>>> menu.displayValue = ['Template']
>>> admin.open(menu.value[0])
>>> admin.getControl('Title').value = 'Zuender'
>>> admin.getControl('Source').value = (
...     '<article><head/><body>'
...     '<a href="http://zuender.zeit.de"><strong>Nach Hause</strong> - '
...     '/Zuender. Das Netzmagazin</a></body></article>')
>>> admin.getControl('Add').click()
>>> print admin.contents
<?xml ...
<!DOCTYPE ...
    <title> Zuender – Edit webdav properties </title>
    ...


Add another template:

>>> admin.getLink('Article templates').click()
>>> menu = admin.getControl(name='add_menu')
>>> menu.displayValue = ['Template']
>>> admin.open(menu.value[0])
>>> admin.getControl('Title').value = 'Extrablatt'
>>> admin.getControl('Source').value = (
...     '<article xmlns:py="http://codespeak.net/lxml/objectify/pytype">'
...     '<head/><body/></article>\n'
...     '<?ZEIT-StyleGroup zeitwissen-extrablatt?>')
>>> admin.getControl('Add').click()
>>> print admin.contents
<?xml ...
<!DOCTYPE ...
    <title> Extrablatt – Edit webdav properties </title>
    ...

Set the default ressort to Studium:

>>> admin.getControl(name='namespace:list').value = (
...     'http://namespaces.zeit.de/CMS/document')
>>> admin.getControl(name='name:list').value = 'ressort'
>>> admin.getControl(name='value:list').value = 'Studium'
>>> admin.getControl('Save').click()

Add another, totally unrelated property, to make sure those are copied to the
article:

>>> admin.getControl(name='namespace:list', index=1).value = (
...     'http://namespaces.zeit.de/my-own-namespace')
>>> admin.getControl(name='name:list', index=1).value = 'hans'
>>> admin.getControl(name='value:list', index=1).value = 'wurst'


When we're now adding an article we can choose those templates:

>>> browser.getLink('online').click()
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Article']
>>> browser.open(menu.value[0])
>>> browser.getControl('Template').displayOptions
['(no value)', 'Extrablatt', 'Zuender']

Create an article with `Extrablatt` template:

>>> browser.getControl('Template').displayValue = ['Extrablatt']
>>> browser.getControl('Continue').click()

As we've choosen extrablatt, the ressort is filled with the changed ressort
now:

>>> browser.getControl('Ressort').displayValue
['Studium']

The other fields, like copyright, which are prefilled by default are still
filled:

>>> browser.getControl('Copyright').value
'ZEIT ONLINE'

Now fill in the actual article:

>>> browser.getControl('File name').value = 'new-extrablatt'
>>> browser.getControl('Title').value = 'Extrablatt 53'
>>> browser.getControl('Year').value = '2007'
>>> browser.getControl('Volume').value = '49'
>>> browser.getControl(name='form.authors.0.').value = 'Hans Sachs'
>>> browser.getControl(name='form.actions.add').click()
>>> print browser.contents
<?xml ...
<!DOCTYPE ...
    <title> Extrablatt 53 – Edit article </title>
    ...


Let's have a look at the source:

>>> browser.getLink('Source').click()
>>> print browser.getControl('Source').value.replace('\r\n', '\n')
<article xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="year">2007</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="volume">49</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="ressort">Studium</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="author">Hans Sachs</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="copyrights">ZEIT ONLINE</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="DailyNL">yes</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="comments">yes</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="banner">yes</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="mostread">yes</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="paragraphsperpage">7</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="has_recensions">no</attribute>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document" name="artbox_thema">no</attribute>
  </head>
  <body>
    <title>Extrablatt 53</title>
  </body>
</article>
<?ZEIT-StyleGroup zeitwissen-extrablatt?>


Javascript validations
======================

The teaser fields are limited in length. They have special widgets which
prevent entering more than the allowed length. Makre sure the widget is used:

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Article']
>>> browser.open(menu.value[0])
>>> browser.getControl('Continue').click()
>>> print browser.contents
<?xml ...
<!DOCTYPE ...
    <title> 01 – Add article </title>...
        <div class="widget"><div class="show-input-limit" maxlength="170"></div><textarea cols="60" id="form.teaserText" name="form.teaserText" rows="15" ></textarea><script type="text/javascript">new zeit.cms.InputValidation("form.teaserText");</script></div>
        ...
        <div class="widget"><div class="show-input-limit" maxlength="20"></div><textarea cols="60" id="form.shortTeaserTitle" name="form.shortTeaserTitle" rows="15" ></textarea><script type="text/javascript">new zeit.cms.InputValidation("form.shortTeaserTitle");</script></div>
        ...
        <div class="widget"><div class="show-input-limit" maxlength="50"></div><textarea cols="60" id="form.shortTeaserText" name="form.shortTeaserText" rows="15" ></textarea><script type="text/javascript">new zeit.cms.InputValidation("form.shortTeaserText");</script></div>
        ...



.. [1] Create an infobox

    >>> import zope.app.component.hooks
    >>> old_site = zope.app.component.hooks.getSite()
    >>> zope.app.component.hooks.setSite(getRootFolder())

    Create the infobox

    >>> import zeit.cms.repository.interfaces
    >>> repository = zope.component.getUtility(
    ...     zeit.cms.repository.interfaces.IRepository)
    >>> import zeit.content.infobox.infobox
    >>> infobox = zeit.content.infobox.infobox.Infobox()
    >>> infobox.supertitle = u'Altersvorsorge'
    >>> import zope.publisher.browser
    >>> import zope.security.testing
    >>> principal = zope.security.testing.Principal('bob')
    >>> request = zope.publisher.browser.TestRequest()
    >>> request.setPrincipal(principal)
    >>> import zope.security.management
    >>> zope.security.management.newInteraction(request)
    >>> infobox.contents = (
    ...     ('Informationen', '<p>Nutzen Sie die Renteninformation, etc</p>'),
    ...     ('Fehlende Versicherungszeiten',
    ...      '<p>Pruefen Sie, ob in Ihrer Renteninformation alle</p>'))
    >>> repository['infobox'] = infobox
    >>> zope.security.management.endInteraction()

    Commit the transaction so our browser sees the change. Also unset the site
    again:

    >>> import transaction
    >>> transaction.commit()
    >>> zope.app.component.hooks.setSite(old_site)

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

.. [3] Create an image gallery.

    >>> import zope.app.component.hooks
    >>> old_site = zope.app.component.hooks.getSite()
    >>> zope.app.component.hooks.setSite(getRootFolder())

    Create and add:

    >>> import zeit.content.gallery.gallery
    >>> gallery = zeit.content.gallery.gallery.Gallery()
    >>> repository['gallery'] = gallery

    >>> import transaction
    >>> transaction.commit()
    >>> zope.app.component.hooks.setSite(old_site)


.. [#portraitbox] Create a portraitbox

    >>> import zope.app.component.hooks
    >>> old_site = zope.app.component.hooks.getSite()
    >>> zope.app.component.hooks.setSite(getRootFolder())

    Create and add:

    >>> import zeit.content.portraitbox.portraitbox
    >>> pb = zeit.content.portraitbox.portraitbox.Portraitbox()
    >>> pb.name = 'Harry Hirsch'
    >>> pb.text = 'hirsch'
    >>> repository['pb'] = pb

    >>> import transaction
    >>> transaction.commit()
    >>> zope.app.component.hooks.setSite(old_site)


