=============
Image Gallery
=============

Galleries are basically a document which references a folder containing images.
Create a  browser first:

>>> from z3c.etestbrowser.testing import ExtendedTestBrowser
>>> browser = ExtendedTestBrowser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')


For creating a gallery we need a folder containing images:

>>> from zeit.content.gallery.browser.testing import add_folder, add_image
>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01')
>>> add_folder(browser, 'gallery')
>>> browser.url
'http://localhost/++skin++cms/repository/online/2007/01/gallery/@@view.html'

Add some images to the folder:

>>> add_image(browser, '01.jpg')
'http://localhost/++skin++cms/repository/online/2007/01/gallery/01.jpg/@@view.html'
>>> add_image(browser, '02.jpg')
'http://localhost/++skin++cms/repository/online/2007/01/gallery/02.jpg/@@view.html'
>>> add_image(browser, '03.jpg')
'http://localhost/++skin++cms/repository/online/2007/01/gallery/03.jpg/@@view.html'
>>> add_image(browser, '04.jpg')
'http://localhost/++skin++cms/repository/online/2007/01/gallery/04.jpg/@@view.html'
>>> add_image(browser, '05.jpg')
'http://localhost/++skin++cms/repository/online/2007/01/gallery/05.jpg/@@view.html'


Adding gallery
==============

To add the gallery we go back to 2007/01:

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Gallery']
>>> browser.open(menu.value[0])

Set the most important values:

>>> browser.getControl('File name').value = 'island'
>>> browser.getControl('Title').value = 'Auf den Spuren der Elfen'
>>> browser.getControl('Ressort').displayValue = ['Reisen']
>>> browser.getControl('Daily newsletter').selected = True
>>> browser.getControl(name="form.image_folder").value = (
...     'http://xml.zeit.de/online/2007/01/gallery')
>>> browser.getControl(name='form.authors.0.').value = 'Hans Sachs'
>>> browser.getControl(name="form.actions.add").click()

After adding the gallery we're at the overview page.  The overview page shows
thumbnails of the images in the gallery together with the texts:

>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.user/island/@@overview.html'
>>> print browser.contents
<?xml ...
<!DOCTYPE ...
    <table class="gallery table-sorter">
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/01.jpg/@@raw" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/02.jpg/@@raw" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/03.jpg/@@raw" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/04.jpg/@@raw" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/05.jpg/@@raw" alt="" height="50" width="50" border="0" />
    ...
</table>...

We can edit the metadata of the gallery on the edit tab:

>>> browser.getLink('Edit metadata').click()
>>> browser.getControl('Title').value
'Auf den Spuren der Elfen'
>>> print browser.title.strip()
Auf den Spuren der Elfen – Edit gallery

There is no read only view of the metadata:

>>> browser.getLink('View metadata')
Traceback (most recent call last):
    ...
LinkNotFoundError

>>> browser.getControl('Gallery type').displayValue
['eigenst\xc3\xa4ndig']
>>> browser.getControl('Gallery type').displayValue = ['inline']
>>> browser.getControl('Apply').click()
>>> print browser.contents
<...<div class="summary">Updated on ...
>>> browser.getControl('Gallery type').displayValue
['inline']

The 'text' field enforces a maximum length:

>>> browser.getControl('Text').value = 'a' * 600
>>> browser.getControl('Apply').click()
>>> print browser.contents
<...class="error">Text is to long. Allowed: 560, got: 600...



Editing a gallery
=================

Each entry can be edited on the overview page:

>>> browser.getLink('Images').click()
>>> browser.getLink('Edit image').click()
>>> browser.getControl('Title').value = 'The man man'
>>> browser.getControl('Layout').displayOptions
['(no value)', 'Hidden', 'Image only']
>>> browser.getControl('Layout').displayValue = ['Image only']
>>> browser.getControl('Image caption').value = "Mann/Stein"
>>> browser.getControl('Apply').click()

After saving we're back at the overview:

>>> print browser.contents
<?xml version="1.0"?>...
<div class="caption">Mann/Stein</div>...
<div class="title">The man man</div>...



Images can be re-ordered at the overview via javascript drag and drop. This
basically changes the order of the input fields:

>>> browser.getControl(name='images:list', index=0).value
'01.jpg'
>>> browser.getControl(name='images:list', index=1).value
'02.jpg'

So let's change the sorting:

>>> browser.getControl(name='images:list', index=0).value = '02.jpg'
>>> browser.getControl(name='images:list', index=1).value = '01.jpg'

>>> browser.getControl('Save sorting').click()


>>> print browser.contents
<?xml ...
<!DOCTYPE ...
    <table class="gallery table-sorter">
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/02.jpg/@@raw" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/01.jpg/@@raw" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/03.jpg/@@raw" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/04.jpg/@@raw" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/05.jpg/@@raw" alt="" height="50" width="50" border="0" />
    ...
</table>...

Galleries also have assets:

>>> bookmark = browser.url
>>> browser.getLink('Edit assets').click()
>>> browser.getControl('Add Related')
<SubmitControl name='form.related.add' type='submit'>

The default view while editing a gallery is the overview page:

>>> browser.open('/++skin++cms/workingcopy/zope.user/island')
>>> print browser.title.strip()
Auf den Spuren der Elfen – Overview
>>> import lxml.cssselect
>>> nodes = lxml.cssselect.CSSSelector('.context-views li.images.selected')(
...     browser.etree)
>>> [li.xpath('string(.)').strip() for li in nodes]
['Images']


Reloading the image folder
==========================

Sometimes it will be necessary to manually reload the image folder, i.e. when
images were added. Remove the image 03.jpg from the gallery folder:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/gallery/03.jpg/delete.html')
>>> print browser.contents
<div ...
      Do you really want to delete the object from the folder
      "<span class="containerName">gallery</span>"?
      ...
      <span>03.jpg</span>
      (<span>http://xml.zeit.de/online/2007/01/gallery/03.jpg</span>)
    ...
>>> browser.getControl("Delete").click()

Now as the image is removed, go back to the gallery, the 03.jpg is no longer
listed:

>>> browser.open(bookmark)
>>> print browser.contents
<?xml ...
<!DOCTYPE ...
    <table class="gallery table-sorter">
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/02.jpg/@@raw" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/01.jpg/@@raw" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/04.jpg/@@raw" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/05.jpg/@@raw" alt="" height="50" width="50" border="0" />
    ...
</table>...

>>> '03.jpg' in browser.contents
False


Sadly the xml is not updated, yet:

>>> browser.getLink('Source').click()
>>> print browser.getControl('XML Source').value.replace('\r\n', '\n')
<gallery xmlns:py="http://codespeak.net/lxml/objectify/pytype">
    ...
        <block name="03.jpg">
        <text xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
          <image ... align="left" src="http://xml.zeit.de/online/2007/01/gallery/03.jpg" type="jpg"...>
            <bu xsi:nil="true"/>
            <copyright py:pytype="str" link="http://www.zeit.de/">ZEIT ONLINE</copyright>
          </image>
          <thumbnail ...align="left" src="http://xml.zeit.de/online/2007/01/gallery/thumbnails/03.jpg" type="jpg"...>
            <bu xsi:nil="true"/>
            <copyright py:pytype="str" link="http://www.zeit.de/">ZEIT ONLINE</copyright>
          </thumbnail>
        </block>
        ...
</gallery>


So synchronise with the image folder:

>>> browser.getLink('Synchronise with image folder').click()
>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.user/island/@@overview.html'
>>> print browser.contents
<?xml ...
        <li class="message">Image folder was synchronised.</li>
        ...
>>> browser.getLink('Source').click()
>>> '03.jpg' in browser.getControl('XML Source').value
False


Synchronising the image folder is also necessary when the metadata (especially
the caption) of the image changes:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/'
...     'gallery/01.jpg/@@view.html')
>>> browser.getLink('Checkout').click()
>>> browser.getControl('Image sub text').value = 'Bite my shiny metal ass'
>>> browser.getControl('Apply').click()
>>> browser.getLink('Checkin').click()
>>> browser.open(bookmark)
>>> browser.getLink('Synchronise with image folder').click()
>>> browser.getLink('Source').click()
>>> print browser.getControl('XML Source').value.replace('\r\n', '\n')
<gallery...
        <block layout="image-only" name="01.jpg">
          ...
          <caption...>Mann/Stein</caption>
          <image ... src="http://xml.zeit.de/online/2007/01/gallery/01.jpg" ...
            <bu ...>Bite my shiny metal ass</bu>...
          </image>
          <thumbnail ...
            <bu ...>Bite my shiny metal ass</bu>...
          </thumbnail>
        </block>
        ...


The redirect of the synchronise view can be prevented by passing an argument.
The url where it would have redirected to will be returned:

>>> url = browser.getLink('Synchronise with image folder').url
>>> browser.open(url + '?redirect=false')
>>> print browser.contents
http://localhost/++skin++cms/workingcopy/zope.user/island/@@overview.html
>>> browser.open(browser.contents)

Checkin
=======

Check in the gallery:

>>> browser.getLink('Checkin').click()

We now have a view tab:

>>> browser.getLink('View metadata').click()
>>> print browser.title.strip(),
Auf den Spuren der Elfen – View gallery metadata

There is also a metdata preview showing the images:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/island'
...     '/@@metadata_preview')
>>> print browser.contents
<div ...
    <div class="image-group-image-preview">
      <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/02.jpg/thumbnail" alt="" height="100" width="100" border="0" />
    </div>
    <div class="image-group-image-preview">
      <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/01.jpg/thumbnail" alt="" height="100" width="100" border="0" />
    </div>
    <div class="image-group-image-preview">
      <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/04.jpg/thumbnail" alt="" height="100" width="100" border="0" />
    </div>
    <div class="image-group-image-preview">
      <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/05.jpg/thumbnail" alt="" height="100" width="100" border="0" />
    </div>
    ...


The default view while a gallery is checked in, is the metadata page:

>>> browser.open('/++skin++cms/repository/online/2007/01/island')
>>> print browser.title.strip()
Auf den Spuren der Elfen – View gallery metadata
>>> nodes = lxml.cssselect.CSSSelector(
...     '.context-views li.view_metadata.selected')(browser.etree)
>>> [li.xpath('string(.)').strip() for li in nodes]
['View metadata']


Browsing location
=================

The browsing location for an image gallery is
/bilder/jahr/ausgab/bildergalerien.  We verify that in python so we need some
setup:

>>> import zope.app.component.hooks
>>> old_site = zope.app.component.hooks.getSite()
>>> zope.app.component.hooks.setSite(getRootFolder())
>>>
>>> import zope.component
>>> import zeit.cms.repository.interfaces
>>> import zeit.cms.browser.interfaces
>>> import zeit.content.gallery.interfaces
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> def get_location(obj):
...     return zope.component.getMultiAdapter(
...         (obj, zeit.content.gallery.interfaces.galleryFolderSource),
...         zeit.cms.browser.interfaces.IDefaultBrowsingLocation).uniqueId
>>> import zeit.connector.interfaces
>>> connector = zope.component.getUtility(
...     zeit.connector.interfaces.IConnector)
>>> connector.changeProperties(
...     'http://xml.zeit.de/',
...     {('base-folder', 'http://namespaces.zeit.de/CMS/Image'):
...      'http://xml.zeit.de/bilder'})


For the island gallery we currently have its container as location, because the
image folder doesn't exist:

>>> gallery = repository['online']['2007']['01']['island']
>>> gallery
<zeit.content.gallery.gallery.Gallery object at 0x...>
>>> get_location(gallery)
u'http://xml.zeit.de/online/2007/01'

Create the image folder:

>>> browser.open('http://localhost/++skin++cms/repository')
>>> add_folder(browser, 'bilder')
>>> add_folder(browser, '2008')
>>> add_folder(browser, '26')
>>> add_folder(browser, 'bildergalerien')

We get the right location now:

>>> get_location(gallery)
u'http://xml.zeit.de/bilder/2008/26/bildergalerien'

For add forms we need to make sure we'll get the right location on the folder:

>>> get_location(gallery.__parent__)
u'http://xml.zeit.de/bilder/2008/26/bildergalerien'

Clean up:

>>> zope.app.component.hooks.setSite(old_site)
