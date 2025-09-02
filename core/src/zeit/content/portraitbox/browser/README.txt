Portraitbox UI
==============

Create a testbrowser first:

>>> from zeit.cms.testing import Browser
>>> browser = Browser(layer['wsgi_app'])
>>> browser.login('user', 'userpw')

>>> import zope.component
>>> import zeit.cms.repository.interfaces
>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> repository['image'] = zeit.content.image.testing.create_local_image()

Lets create a portraitbox:

>>> browser.open('http://localhost/++skin++cms/repository')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Portraitbox']
>>> browser.open(menu.value[0])

We are now at the add form. Set the filename:

>>> browser.getControl('File name').value = 'Wurst-Hans'

The infobox has a name and html content:

>>> browser.getControl('First and last name').value = 'Hans Wurst'
>>> browser.getControl('Text').value = (
...     '<p><strong>HW</strong> is in da house</p>')

Reference an image:

>>> browser.getControl('Image').value = 'http://xml.zeit.de/image'

Finnaly add the portraitbox:

>>> browser.getControl('Add').click()


We're now at the edit form:

>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.user/Wurst-Hans/@@edit.html'

Make sure the box is listed in the workingcopy panel:

>>> print(browser.contents)
<...
    <li class="draggable-content type-portraitbox">
      <img src="...zmi_icon.png"...
      <a href="http://localhost/++skin++cms/workingcopy/zope.user/Wurst-Hans/...">Hans Wurst</a>...


Verify the source:

>>> browser.getLink('Source').click()
>>> print(browser.getControl('Source').value)
<container... layout="artbox" label="portrait">
  <block>
    <title...>Hans Wurst</title>
    <image ...src="http://xml.zeit.de/image" type="jpeg"/>
    <text>
      <p><strong>HW</strong> is in da house</p>
    </text>
  </block>
</container>


Let's check it in:

>>> browser.getLink('Checkin').click()
>>> print(browser.title.strip())
Hans Wurst – View source code


Make sure there is a metadata preview:

>>> browser.url
'http://localhost/++skin++cms/repository/Wurst-Hans/...'
>>> browser.open(
...     'http://localhost/++skin++cms/repository/'
...     'Wurst-Hans/@@metadata_preview')
>>> print(browser.contents)
 <div class="contextViewsAndActions">
    <div class="context-views">
    ...
    <div class="title">Hans Wurst</div>
    ...

Make sure an box has a default view:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/Wurst-Hans')
>>> print(browser.contents)
<?xml ...
    <title> Hans Wurst – View portraitbox </title>
    ...



Browsing location
=================

Setup
-----

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> import zope.component
>>> import zeit.cms.repository.interfaces
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)

>>> import zeit.cms.content.interfaces
>>> source = zope.component.getUtility(
...     zeit.cms.content.interfaces.ICMSContentSource,
...     name='zeit.content.portraitbox')
>>> def get_location(obj):
...     return zope.component.getMultiAdapter(
...         (obj, source),
...         zeit.cms.browser.interfaces.IDefaultBrowsingLocation).uniqueId


For the portraitbox the default browsing location is `/personen` if the folder
exists. Currently it doesn't exist:

>>> obj = repository['testcontent']
>>> get_location(obj)
'http://xml.zeit.de/'

Create the personen folder:

>>> import zeit.cms.repository.folder
>>> repository['personen'] = zeit.cms.repository.folder.Folder()

The location is the `/personen` folder now:

>>> get_location(obj)
'http://xml.zeit.de/personen'

>>> import zope.security.proxy
>>> ref = zeit.content.portraitbox.interfaces.IPortraitboxReference(
...     zope.security.proxy.ProxyFactory(obj))
>>> get_location(ref)
'http://xml.zeit.de/personen'
