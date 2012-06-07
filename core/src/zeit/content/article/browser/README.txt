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
<Link text='View...' ...>


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


Since we have a new article editor a lot of basic tests were removed such as
edit-metadata, wysiwyg, etc. pp

When a new article is created, its body already contains an image block,
so the user is nuged to put an image there (or explicitly decide they don't
want one):

>>> browser.getLink('Source').click()
>>> print browser.getControl('Source').value.replace('\r\n', '\n')
<article xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  ...
  <body>
    <division...
      <image...
</article>

Checking in
===========

Checking in requires the article to be valid:

>>> import zeit.cms.testing
>>> import zeit.cms.workingcopy.interfaces
>>> with zeit.cms.testing.site(getRootFolder()):
...     with zeit.cms.testing.interaction():
...         wc = zeit.cms.workingcopy.interfaces.IWorkingcopy(None)
...         article = list(wc.values())[0]
...         article.title = u'Title'
...         article.ressort = u'Deutschland'

We check in the document. We look at the document in the repository then:

>>> browser.reload()  # reload to show the checkin link
>>> browser.getLink('Checkin').click()
>>> article_url = browser.url
>>> article_url
'http://localhost/++skin++cms/repository/.../...tmp/@@xml_source_view.html'

A checked in article has a link that offers a basic view:

>>> browser.getLink('View')
<Link...'http://localhost/++skin++cms/repository/.../...tmp/@@edit.html'>

It will have a menu for the source
>>> browser.getLink('View source')
<Link...http://localhost/++skin++cms/repository/.../...tmp/@@xml_source_view.html'>


It will have a menu for references
>>> browser.getLink('References')
<Link...http://localhost/++skin++cms/repository/.../...tmp/@@references.html'>

When we checkout the article we will get the following
>>> browser.getLink('View').click()
>>> browser.getLink('Checkout').click()
>>> article_url = browser.url
>>> article_url
'http://localhost/++skin++cms/workingcopy/.../...tmp/@@edit.html'

The edit source link...
>>> browser.getLink('Source')
<Link...@@xml_source_edit.html'>

...and the references
>>> browser.getLink('References')
<Link...@@references.html'>

There was a bug once where after editing an article there were edit fields on
the read only form:

>>> browser.getControl('Teaser text')
Traceback (most recent call last):
    ...
LookupError: label 'Teaser text'
