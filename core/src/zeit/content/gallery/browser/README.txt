=============
Image Gallery
=============

Galleries are basically a document which references a folder containing images.
Create a  browser first:

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')


For creating a gallery we need a folder containing images:

>>> def add_folder(name):
...     menu = browser.getControl(name='add_menu')
...     menu.displayValue = ['Folder']
...     browser.open(menu.value[0])
...     browser.getControl('File name').value = name
...     browser.getControl('Add').click()
...
>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01')
>>> add_folder('gallery')
>>> browser.url
'http://localhost/++skin++cms/repository/online/2007/01/gallery/@@view.html'


Add some images to the folder:

>>> import os.path
>>> def add_image(name):
...     menu = browser.getControl(name='add_menu')
...     menu.displayValue = ['Image (single)']
...     browser.open(menu.value[0])
...     test_file = os.path.join(os.path.dirname(__file__),
...                              'testdata', name)
...     test_data = open(test_file, 'rb')
...     file_control = browser.getControl(name='form.blob')
...     file_control.add_file(test_data, 'image/jpeg', name)
...     browser.getControl(name='form.copyrights.0..combination_00').value = (
...         'ZEIT ONLINE')
...     browser.getControl(name='form.copyrights.0..combination_01').value = (
...         'http://www.zeit.de/')
...     browser.getControl(name='form.actions.add').click()
...     browser.getLink('Checkin').click() 
...     url = browser.url
...     browser.getLink('gallery').click()
...     return url
...
>>> add_image('01.jpg')
'http://localhost/++skin++cms/repository/online/2007/01/gallery/01.jpg/@@view.html'
>>> add_image('02.jpg')
'http://localhost/++skin++cms/repository/online/2007/01/gallery/02.jpg/@@view.html'
>>> add_image('03.jpg')
'http://localhost/++skin++cms/repository/online/2007/01/gallery/03.jpg/@@view.html'
>>> add_image('04.jpg')
'http://localhost/++skin++cms/repository/online/2007/01/gallery/04.jpg/@@view.html'
>>> add_image('05.jpg')
'http://localhost/++skin++cms/repository/online/2007/01/gallery/05.jpg/@@view.html'


Adding gallery
==============

To add the gallery we go back to 2007/01:

>>> browser.getLink('01').click()
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
    <table class="gallery">
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/01.jpg" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/02.jpg" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/03.jpg" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/04.jpg" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/05.jpg" alt="" height="50" width="50" border="0" />
    ...
</table>...

We can edit the metadata of the gallery on the edit tab:

>>> browser.getLink('Edit metadata').click()
>>> browser.getControl('Title').value
'Auf den Spuren der Elfen'
>>> print browser.contents
<?xml ...
<!DOCTYPE html ...
    <title> Auf den Spuren der Elfen – Edit gallery </title>
    ...

There is no read only view of the metadata:

>>> browser.getLink('View metadata')
Traceback (most recent call last):
    ...
LinkNotFoundError



Editing a gallery
=================

Each entry can be edited on the overview page:

>>> browser.getLink('Images').click()
>>> browser.getLink('01.jpg').click()
>>> browser.getControl('Title').value = 'The man man'
>>> browser.getControl('Text').value = (
...     '<p><strong>Der Mann am Stein</strong></p>')
>>> browser.getControl('Layout').displayOptions
['(no value)', 'Image only']
>>> browser.getControl('Layout').displayValue = ['Image only']
>>> browser.getControl('Image caption').value = "Mann/Stein"
>>> browser.getControl('Apply').click()

After saving we're back at the overview:

>>> print browser.contents
<?xml ...
  <tr>
    <td class="image-column">
      <input type="hidden" ...
      <a title="Show image"
       href="http://localhost/++skin++cms/repository/online/2007/01/gallery/01.jpg/@@view.html">
       <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/01.jpg" alt="" height="50" width="50" border="0" />
     </a>
      <a href="http://localhost/++skin++cms/workingcopy/zope.user/island/01.jpg"
        title="Edit">
        <div class="image-name">01.jpg</div>
      </a>
    </td>
    <td>
      <div class="caption">Mann/Stein</div>
      <div class="title">The man man</div>
      <div class="text"><p> <strong>Der Mann am Stein</strong> </p> </div>
    </td>
  </tr>
  ...


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
    <table class="gallery">
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/02.jpg" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/01.jpg" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/03.jpg" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/04.jpg" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/05.jpg" alt="" height="50" width="50" border="0" />
    ...
</table>...


Reloading the image folder
==========================

Sometimes it will be necessary to manually reload the image folder, i.e. when
images were added. Remove the image 03.jpg from the gallery folder:

>>> bookmark = browser.url
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
    <table class="gallery">
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/02.jpg" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/01.jpg" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/04.jpg" alt="" height="50" width="50" border="0" />
    ...
        <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/05.jpg" alt="" height="50" width="50" border="0" />
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
          <image xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" align="left" src="http://xml.zeit.de/online/2007/01/gallery/03.jpg" type="jpg">
            <bu xsi:nil="true"/>
            <copyright py:pytype="str" link="http://www.zeit.de/">ZEIT ONLINE</copyright>
          </image>
          <thumbnail xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" align="left" src="http://xml.zeit.de/online/2007/01/gallery/thumbnails/03.jpg" type="jpg">
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

Galleries also have assets:

>>> browser.getLink('Edit assets').click()
>>> browser.getControl('Add Related')
<SubmitControl name='form.related.add' type='submit'>


Checkin
=======

Check in the gallery:

>>> browser.getLink('Checkin').click()

We now have a view tab:

>>> browser.getLink('View metadata').click()
>>> print browser.contents
<?xml ...
<!DOCTYPE html ...
    <title> Auf den Spuren der Elfen – View gallery metadata </title>
    ...

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
>>> add_folder('bilder')
>>> add_folder('2008')
>>> add_folder('26')
>>> add_folder('bildergalerien')

We get the right location now:

>>> get_location(gallery)
u'http://xml.zeit.de/bilder/2008/26/bildergalerien'

For add forms we need to make sure we'll get the right location on the folder:

>>> get_location(gallery.__parent__)
u'http://xml.zeit.de/bilder/2008/26/bildergalerien'

Clean up:

>>> zope.app.component.hooks.setSite(old_site)
