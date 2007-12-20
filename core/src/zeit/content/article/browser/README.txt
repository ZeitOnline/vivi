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
    <div class="context-views">...
    <div class="context-actions">...
    <div id="metadata_preview">...
      <div class="teaser-title" title="Teaser">...

>>> browser.getLink('Checkout')
<Link text='[IMG] Checkout' ...>

Make sure we have a "view" link:

>>> browser.getLink('View')
<Link text='View metadata' ...>


We have to publish another url to see if articles are listed:

>>> browser.handleErrors = False
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
'http://localhost/++skin++cms/repository/online/2007/01/@@zeit.content.article.ChooseTemplate'
>>> browser.open(menu.value[0])

We now need to choose a template. Since we haven't created one there is only
the (no value) to be choosen. 

>>> browser.getControl('Template').displayOptions
['(no value)']
>>> browser.getControl('Template').displayValue
['(no value)']
>>> browser.handleErrors = False
>>> browser.getControl('Continue').click()

We are now looking at the add form. Some fields are filled with suitable
defaults:

>>> print browser.contents
<?xml ...
<!DOCTYPE ...
    <title> Add article </title>
    ...

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

After submitting we're looking at the object in our working copy. The metadata
edit screen should be displayed:

>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.mgr/KFZ-Steuer/@@edit.html'
>>> print browser.contents
<?xml ...
<!DOCTYPE ...
    <title> Edit article </title>
    ...

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


Let's add an image:

>>> browser.getControl('Add Images').click()
>>> browser.getControl(name="form.images.0.").value = (
...     'http://xml.zeit.de/2006/DSC00109_2.JPG')
>>> browser.getControl('Apply').click()
>>> 'There were errors' in browser.contents
False


Checking in 
===========

We check in the document. We look a the document in the repository then:

>>> browser.getLink('Checkin').click()
>>> article_url = browser.url
>>> article_url
'http://localhost/++skin++cms/repository/.../KFZ-Steuer/@@view.html'


Let's make sure the image is linked:

>>> print browser.contents 
<?xml ...
<!DOCTYPE ...
 <div class="widget"><ol class="sequenceWidget" >
 <li><a href="http://localhost/++skin++cms/repository/2006/DSC00109_2.JPG">DSC00109_2.JPG</a></li>
 </ol></div>
  ...

After checking in we also do not have an edit metadata link:

>>> browser.getLink('Edit metadata')
Traceback (most recent call last):
    ...
LinkNotFoundError


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
>>> browser.getLink('Source').click()
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
>>> browser.getLink('Source').click()
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

>>> browser.getLink('Edit metadata').click()
>>> browser.getControl(name='form.teaserTitle').value = 'Trinker zur Kasse'
>>> browser.getControl('Apply').click()
>>> browser.getLink('Checkin').click()

Now the feed has been changed. Verify this by checking out the feed and looking
at its xml source:

>>> browser.open('http://localhost/++skin++cms/repository/politik.feed')
>>> browser.getLink('Checkout').click()
>>> browser.getLink('Source').click()
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


>>> browser.getLink('Templates').click()
>>> browser.getLink('Article templates').click()
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Template']
>>> browser.open(menu.value[0])
>>> browser.getControl('Title').value = 'Zuender'
>>> browser.getControl('Source').value = (
...     '<article><head/><body>'
...     '<a href="http://zuender.zeit.de"><strong>Nach Hause</strong> - '
...     '/Zuender. Das Netzmagazin</a></body></article>')
>>> browser.getControl('Add').click()
>>> print browser.contents
<?xml ...
<!DOCTYPE ...
    <title> Edit webdav properties </title>
    ...


Add another template:

>>> browser.getLink('Article templates').click()
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Template']
>>> browser.open(menu.value[0])
>>> browser.getControl('Title').value = 'Extrablatt'
>>> browser.getControl('Source').value = (
...     '<article><head/><body/></article>\n'
...     '<?ZEIT:StyleGroup zeitwissen-extrablatt?>')
>>> browser.getControl('Add').click()
>>> print browser.contents
<?xml ...
<!DOCTYPE ...
    <title> Edit webdav properties </title>
    ...

Set the default ressort to Extrablatt:

>>> browser.getControl(name='namespace:list').value = (
...     'http://namespaces.zeit.de/CMS/document')
>>> browser.getControl(name='name:list').value = 'ressort'
>>> browser.getControl(name='value:list').value = 'Extrablatt'
>>> browser.getControl('Save').click()

Add another, totally unrelated property, to make sure those are copied to the
article:

>>> browser.getControl(name='namespace:list', index=1).value = (
...     'http://namespaces.zeit.de/my-own-namespace')
>>> browser.getControl(name='name:list', index=1).value = 'hans'
>>> browser.getControl(name='value:list', index=1).value = 'wurst'


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

>>> browser.getControl('Ressort').value
'Extrablatt'

The other fields, like copyright, which are prefilled by default are still
filled:

>>> browser.getControl('Copyright').value
'ZEIT online'

Now fill in the actual article:

>>> browser.getControl('File name').value = 'new-extrablatt'
>>> browser.getControl('Title').value = 'Extrablatt 53'
>>> browser.getControl('Year').value = '2007'
>>> browser.getControl('Volume').value = '49'
>>> browser.getControl(name='form.actions.add').click()
>>> print browser.contents
<?xml ...
<!DOCTYPE ...
    <title> Edit article </title>
    ...


Let's hae a look at the source:

>>> browser.getLink('Source').click()
>>> print browser.getControl('Source').value.replace('\r\n', '\n')
<article>
  <head>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="year">2007</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="volume">49</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="copyrights">ZEIT online</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="comments">true</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="banner">true</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="mostread">true</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="ressort"> </attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="paragraphsperpage">6</attribute>
    <attribute ns="http://namespaces.zeit.de/CMS/document" name="DailyNL">false</attribute>
  </head>
  <body>
    <title>Extrablatt 53</title>
  </body>
</article><?ZEIT:StyleGroup zeitwissen-extrablatt?>




Javascript validations
======================

Javascript validations are provided by gocept.form mainly. But make sure
they're actually here:

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Article']
>>> browser.open(menu.value[0])
>>> browser.getControl('Continue').click()
>>> print browser.contents
<?xml ...
<!DOCTYPE ...
    <title> Add article </title>...
        <script language="javascript">
// max-length
connect(window, "onload", function(event) {new gocept.validation.MaxLength('form.teaserText', 170, "Too long (max 170)")});
// max-length
connect(window, "onload", function(event) {new gocept.validation.MaxLength('form.shortTeaserTitle', 20, "Too long (max 20)")});
// max-length
connect(window, "onload", function(event) {new gocept.validation.MaxLength('form.shortTeaserText', 50, "Too long (max 50)")});
</script>
    ...
