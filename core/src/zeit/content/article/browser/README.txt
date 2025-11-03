==========
Article UI
==========

For UI-Tests we need a Testbrowser:

>>> from zeit.cms.testing import Browser
>>> browser = Browser(layer['wsgi_app'])
>>> browser.login('user', 'userpw')

Metadata Preview
================

The metadata preview shows the most important data in list views:

>>> browser.open('/repository/article/metadata_preview')
>>> print(browser.contents)
 <div class="contextViewsAndActions">
    <div class="context-views">...
    <div class="context-actions">...
    <div id="metadata_preview">...
      <div class="teaser-title" title="Title">...

>>> browser.getLink('Checkout')
<Link text='Checkout...>

Make sure we have a "view" link:

>>> browser.getLink('View')
<Link text='View...' ...>


Creating Articles
=================

Articles can be created through the add menu in the repository. We open an
arbitrary url and add an article then:

>>> browser.open('/repository')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Article']
>>> url = menu.value[0]
>>> print(url)
http://localhost/++skin++vivi/repository/@@zeit.content.article.Add
>>> browser.open(url)

The article is created and checked out automatically. The editor is open:

>>> print(browser.title.strip())
e0135811-d21a-4e29-918e-1b0dde4e0c38.tmp – Edit
>>> print(browser.url)
http://localhost/++skin++vivi/workingcopy/zope.user/e0135811-d21a-4e29-918e-1b0dde4e0c38.tmp/@@edit.html


Since we have a new article editor a lot of basic tests were removed such as
edit-metadata, wysiwyg, etc. pp

When a new article is created, its body already contains an image block,
so the user is nuged to put an image there (or explicitly decide they don't
want one):

>>> browser.getLink('Source').click()
>>> print(browser.getControl('Source').value.replace('\r\n', '\n'))
<article>
  ...
  <body>
    ...
    <division...<image...
</article>

Checking in
===========

Checking in requires the article to be valid:

>>> import zeit.cms.tagging.interfaces
>>> import zeit.cms.testing
>>> import zeit.cms.workingcopy.interfaces
>>> import zope.component
>>> from zeit.cms.repository.interfaces import IAutomaticallyRenameable
>>> wl = zope.component.getUtility(zeit.cms.tagging.interfaces.IWhitelist)
>>> with zeit.cms.testing.site(getRootFolder()):
...     with zeit.cms.testing.interaction():
...         wc = zeit.cms.workingcopy.interfaces.IWorkingcopy(None)
...         article = list(wc.values())[0]
...         article.title = 'Title'
...         article.ressort = 'Deutschland'
...         article.keywords = (
...             wl.get('Testtag'), wl.get('Testtag2'), wl.get('Testtag3'),)
...         IAutomaticallyRenameable(article).rename_to = 'asdf'

We check in the document. We look at the document in the repository then:

>>> browser.reload()  # reload to show the checkin link
>>> browser.handleErrors = False
>>> browser.getLink('Checkin').click()
>>> article_url = browser.url
>>> article_url
'http://localhost/++skin++vivi/repository/asdf/@@xml_source_view.html'

A checked in article has a link that offers a basic view:

>>> browser.getLink('View')
<Link...'http://localhost/++skin++vivi/repository/asdf/@@edit.html'>

It will have a menu for the source
>>> browser.getLink('View source')
<Link...http://localhost/++skin++vivi/repository/asdf/@@xml_source_view.html'>


When we checkout the article we will get the following
>>> browser.getLink('View').click()
>>> browser.getLink('Checkout').click()
>>> article_url = browser.url
>>> article_url
'http://localhost/++skin++vivi/workingcopy/zope.user/asdf/@@edit.html'

The edit source link...
>>> browser.getLink('Source')
<Link...@@xml_source_edit.html'>

There was a bug once where after editing an article there were edit fields on
the read only form:

>>> browser.getControl('Teaser text')
Traceback (most recent call last):
    ...
LookupError: label 'Teaser text'...
