=============
Image Gallery
=============

Galleries are basically a document which references a folder containing images.
Create a  browser first:

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')


For creating a gallery we need a folder containing images:


>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Folder']
>>> browser.open(menu.value[0])
>>> browser.getControl('File name').value = 'gallery'
>>> browser.getControl('Add').click()
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
...     test_data = file(test_file, 'rb')
...     file_control = browser.getControl(name='form.data')
...     file_control.filename = name
...     file_control.value = test_data
...     browser.getControl('Add').click()
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
    <title> Edit gallery </title>
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
>>> browser.getControl('Text').value = 'Der Mann am Stein'
>>> browser.getControl('Apply').click()

After saving we're back at the overview:

>>> print browser.contents
<?xml ...
  <tr>
    <td class="image-column">
      <input type="hidden" ...
      <img src="http://localhost/++skin++cms/repository/online/2007/01/gallery/thumbnails/01.jpg" alt="" height="50" width="50" border="0" />
      <a href="http://localhost/++skin++cms/workingcopy/zope.user/island/01.jpg"
        title="Edit">
        <div class="image-name">01.jpg</div>
      </a>
    </td>
    <td>
      <div class="title">The man man</div>
      <div class="text">Der Mann am Stein</div>
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
...     'http://localhost/++skin++cms/repository/online/2007/01/gallery/03.jpg/@@view.html')
>>> browser.getLink("Delete").click()
>>> print browser.contents
<?xml ...
<!DOCTYPE ...
    Do you really want to delete: <b>03.jpg</b>
    ...
>>> browser.getControl("Yes, delete it.").click()

Now as the image is removed, go back to the gallery, the 03.jpg is no longer
listed:

>>> browser.handleErrors = False
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
>>> print browser.getControl('XML Source').value
<centerpage>
    ...
        <block name="03.jpg">
          <text/>
          <image src="http://xml.zeit.de/online/2007/01/gallery/03.jpg" type="jpeg">
            <bu xmlns:ns0="http://www.w3.org/2001/XMLSchema-instance" ns0:nil="true"/>
            <copyright>ZEIT online</copyright>
          </image>
          <thumbnail src="http://xml.zeit.de/online/2007/01/gallery/thumbnails/03.jpg" type="jpeg">
            <bu xmlns:ns0="http://www.w3.org/2001/XMLSchema-instance" ns0:nil="true"/>
            <copyright>ZEIT online</copyright>
          </thumbnail>
        </block>
        ...
</centerpage>


So synchronise with the image folder:

>>> browser.getLink('Synchronise with image folder').click()
>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.user/island/@@overview.html'
>>> browser.getLink('Source').click()
>>> '03.jpg' in browser.getControl('XML Source').value
False


Checkin
=======

Check in the gallery:

>>> browser.getLink('Checkin').click()

We now have a view tab:

>>> browser.getLink('View metadata').click()
>>> print browser.contents
<?xml ...
<!DOCTYPE html ...
    <title> View gallery metadata </title>
    ...
