=====
Image
=====

Create a browser first:

>>> import zope.testbrowser.testing
>>> browser = zope.testbrowser.testing.Browser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')

Listing
========

There is an image in the repository. Get the listing:

>>> browser.open('http://localhost/++skin++cms/repository/2006')
>>> print browser.contents
<?xml ...
  ...<span class="URL">http://localhost/.../DSC00109_2.JPG</span>...


Now we get the metadata preview:

>>> browser.open('http://localhost/++skin++cms/repository/2006/'
...              'DSC00109_2.JPG/@@metadata_preview')
>>> print browser.contents
 <div class="contextViewsAndActions">
    <div class="context-views">
      ...
      <div class="image-metadata">
        <img src=".../2006/DSC00109_2.JPG/metadata-preview" alt=""
               height="90" width="120" border="0" />
        <div>image/jpeg</div>
      <div>
          2048x1536
      </div>
     <div></div>
    ...


Image Data
==========

We get the image itself just by accessing its url:

>>> image = zope.testbrowser.testing.Browser()
>>> image.addHeader('Authorization', 'Basic user:userpw')
>>> image.open(
...     'http://localhost/++skin++cms/repository/2006/DSC00109_2.JPG/@@index.html')
>>> image.headers['content-type']
'image/jpeg'
>>> image.contents[:16]
'\xff\xd8\xff\xe1\x0c\xdaExif\x00\x00MM\x00*'

We also have a preview version of an images. The preview is scaled down on the
server:

>>> image.open('http://localhost/++skin++cms/repository/'
...            '2006/DSC00109_2.JPG/@@preview')
>>> image.headers['content-type']
'image/jpeg'

And a thumbnail is also scaled on the server:

>>> image.open('http://localhost/++skin++cms/repository/'
...            '2006/DSC00109_2.JPG/@@thumbnail')
>>> image.headers['content-type']
'image/jpeg'


Editing
=======

For editing an image, we need to check it out:

>>> browser.getLink('Checkout').click()

We now see the form. The image did not have any metadata prefilled. The
copyright is filled with the default value though:

>>> browser.getControl(name='form.copyrights.0..combination_00').value
'\xc2\xa9'
>>> browser.getControl(name='form.copyrights.0..combination_01').value
''

Fill out some values:

>>> import os
>>> test_file = os.path.join(
...     os.path.dirname(__file__), 'testdata', 'opernball.jpg')
>>> test_data = file(test_file, 'rb')
>>> file_control = browser.getControl(name='form.blob')
>>> file_control.add_file(test_data, 'image/jpeg', 'opernball.jpg')
>>> browser.getControl('Image title').value = 'Opernball'
>>> browser.getControl('Year').value = '2007'
>>> browser.getControl('Volume').value = '9'
>>> browser.getControl('Alternative').value = 'Zwei Taenzer'
>>> browser.getControl('Image sub text').value = 'Tanz beim Opernball'
>>> browser.getControl('Alignment').displayOptions
['left', 'center', 'right']
>>> browser.getControl('Alignment').displayValue = ['center']
>>> browser.getControl('Links to').value = 'http://www.zeit.de'
>>> browser.getControl(name='form.copyrights.0..combination_00').value = (
...     'ZEIT ONLINE')
>>> browser.getControl(name='form.copyrights.0..combination_01').value = (
...     'http://www.zeit.de/')
>>> browser.getControl('Apply').click()
>>> 'There where errors' in browser.contents
False

Verify some values:

>>> browser.getControl(name='form.title').value
'Opernball'
>>> browser.getControl(name='form.year').value
'2007'

Let's verify get the right file data back from the image:

>>> image.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...            'DSC00109_2.JPG/@@index.html')
>>> test_data.seek(0)
>>> image.contents == test_data.read()
True
>>> test_data.close()

Check the image in again:

>>> browser.getLink('Checkin').click()

We have uploaded a new image now. Let's have a look at the metadata screen:

>>> browser.open('http://localhost/++skin++cms/repository/2006/'
...              'DSC00109_2.JPG/@@metadata_preview')
>>> print browser.contents
 <div class="contextViewsAndActions">
    <div class="context-views">...
    <div class="image-metadata">
      <img src=".../2006/DSC00109_2.JPG/metadata-preview" alt=""
            height="90" width="66" border="0" />
      <div>image/jpeg</div>
      <div>
        119x160
      </div>
      <div>Opernball</div>
      ...


When editing an image and not uploading a new image the old image is kept:

>>> browser.open('http://localhost/++skin++cms/repository/2006/'
...              'DSC00109_2.JPG/@@view.html')
>>> browser.getLink('Checkout').click()
>>> browser.getControl(name='form.title').value = 'Opernball in Wien'
>>> browser.getControl('Apply').click()
>>> print browser.contents
<?xml...
    ...Updated on ...

Make sure the image is not changed by looking at the image view:

>>> browser.getLink('View').click()
>>> print browser.contents
<?xml ...
  <title>
    Opernball in Wien – View image
  </title>
  ...
    <tr>
      <td>Dimensions</td>
      <td>
        119x160
      </td>
    </tr>
    <tr>
      <td>Volume/Year</td>
      <td>
        9/2007
      </td>
    </tr>
    <tr>
      <td>Alignment</td>
      <td>center</td>
    </tr>
  ...
  <ol class="image-copyrights">
    <li>
      ZEIT ONLINE
      (<a href="http://www.zeit.de/">http://www.zeit.de/</a>)
    </li>
  </ol>...
      <div>
        Image title: Opernball in Wien
      </div>
      <div>
        ALT: Zwei Taenzer
      </div>
      <div>
        Image sub text: Tanz beim Opernball
      </div>
      <div>
        Links to:
        <a href="http://www.zeit.de">http://www.zeit.de</a>
      </div>
      ...
  


Dragging
========

Try the drag pane:

>>> browser.open('http://localhost/++skin++cms/repository/2006/'
...              'DSC00109_2.JPG/@@drag-pane.html')
>>> print browser.contents
  <img src="http://localhost/++skin++cms/repository/2006/DSC00109_2.JPG/thumbnail" alt="" height="100" width="74" border="0" />
  <div class="Text">Opernball</div>
  <div class="UniqueId">http://xml.zeit.de/2006/DSC00109_2.JPG</div>


Adding
======

Let's add an image:

>>> browser.open('http://localhost/++skin++cms/repository/2006/')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Image (single)']
>>> browser.open(menu.value[0])

The image file is required:

>>> browser.getControl(name='form.copyrights.0..combination_00').value = (
...     'ZEIT ONLINE')
>>> browser.getControl(name='form.copyrights.0..combination_01').value = (
...     'http://www.zeit.de/')
>>> browser.getControl(name='form.actions.add').click()
>>> print browser.contents
<...
<label for="form.blob">
  <span>Upload new image</span>
  <span class="annotation">
    (required)
  </span>
</label>
<div class="hint"></div>
<div class="error">
  <span class="error">Required input is missing.</span>
</div>
...

Load the opernball image data an add w/o setting a file name. This selects the
filename automatically[#no-references]_.

>>> file_control = browser.getControl(name='form.blob')
>>> file_control.add_file(open(test_file, 'rb'), 'image/jpeg', 'opernball.jpg')
>>> browser.getControl(name='form.volume').value != '0'
True
>>> browser.getControl(name='form.actions.add').click()
>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.user/opernball.jpg/@@edit.html'


When editing, the image file is no longer required:

>>> browser.getControl('Image title').value = 'foo'
>>> browser.getControl('Apply').click()
>>> 'Required input is missing' in browser.contents
False

.. [#no-references] There must not be the "references" field on the add form:

    >>> 'Objects using this image' in browser.contents
    False


Image browser
=============

The zeit.content.image package provides an image browser for IFolder:

>>> browser.open('http://localhost/++skin++cms/repository/2006/')
>>> browser.getLink('Images').click()
>>> print browser.contents
<?xml version="1.0"?>
<!DOCTYPE html ...
    <title> 2006 – Images </title>
    ...
    <div id="edit-form" class="image-list">
      <div class="image">
        <div class="image-data">
          <a href="http://localhost/++skin++cms/repository/2006/DSC00109_2.JPG/@@view.html"
             title="Opernball">
            <img src="http://localhost/++skin++cms/repository/2006/DSC00109_2.JPG/thumbnail" alt="" height="100" width="74" border="0" />
          </a>
          <span class="URL">http://localhost/++skin++cms/repository/2006/DSC00109_2.JPG</span>
        </div>
        <div class="image-metadata">
          <div>image/jpeg</div>
          <div>
            119x160
          </div>
        </div>
      </div>
      <div class="image">
        <div class="image-data">
          <a href="http://localhost/++skin++cms/repository/2006/opernball.jpg/@@view.html">
            <img src="http://localhost/++skin++cms/repository/2006/opernball.jpg/thumbnail" alt="" height="100" width="74" border="0" />
          </a>
          <span class="URL">http://localhost/++skin++cms/repository/2006/opernball.jpg</span>
        </div>
        <div class="image-metadata">
          <div>image/jpeg</div>
          <div>
            119x160
          </div>
        </div>
      </div>
    </div>
    ...


Image Groups
============

Image groups group one motif together. This is to have several
shapes/resolutions.

Lets create an image group:

>>> browser.open('http://localhost/++skin++cms/repository/2006/')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Image group']
>>> url = menu.value[0]
>>> browser.open(menu.value[0])
>>> print browser.title.strip()
2006 – Add image group

[#no-references]_

>>> browser.getControl("File name").value = 'new-hampshire'
>>> browser.getControl('Image title').value = 'New Hampshire'
>>> browser.getControl(name='form.copyrights.0..combination_00').value = (
...     'ZEIT ONLINE')
>>> browser.getControl(name='form.copyrights.0..combination_01').value = (
...     'http://www.zeit.de/')
>>> browser.getControl(name='form.actions.add').click()

Image groups are not checked out by default, because adding new images will be
done directly in the repository:

>>> browser.url
'http://localhost/++skin++cms/repository/2006/new-hampshire/@@view.html'
>>> print browser.title.strip()
New Hampshire – Image group

Image groups don't have a thumbnail when there are no images in it:

>>> browser.open('@@thumbnail')
Traceback (most recent call last):
    ...
HTTPError: HTTP Error 404: Not Found
>>> browser.goBack()

Create a few images in the group:

>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Image']
>>> browser.open(menu.value[0])

Images which are added to the group do not have any metadata on adding:

>>> browser.getControl('Title')
Traceback (most recent call last):
    ...
LookupError: label 'Title'

>>> browser.getControl('Volume')
Traceback (most recent call last):
    ...
LookupError: label 'Volume'

Set the file data:

>>> def set_file_data(name):
...     test_file = os.path.join(
...         os.path.dirname(__file__), 'testdata', name)
...     test_data = file(test_file, 'rb')
...     file_control = browser.getControl(name='form.blob')
...     file_control.add_file(test_data, 'image/jpeg', name)

>>> set_file_data('new-hampshire-artikel.jpg')
>>> browser.getControl('Add').click()

After adding the image we're back at the image group:

>>> browser.url
'http://localhost/++skin++cms/repository/2006/new-hampshire'

So we can directly add the next image:

>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Image']
>>> browser.open(menu.value[0])
>>> set_file_data('new-hampshire-450x200.jpg')
>>> browser.getControl('Add').click()

And another one:

>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Image']
>>> browser.open(menu.value[0])
>>> set_file_data('obama-clinton-120x120.jpg')
>>> browser.getControl('Add').click()

Let's have a look at the index:

>>> print browser.contents
<?xml version="1.0"?>
<!DOCTYPE html ...
    <title> New Hampshire – Image group </title>
    ...
  <tbody>
  <tr class="odd">
    ...
    <td>
      new-hampshire-450x200.jpg
    </td>
    <td>
      450x200
    </td>
    <td>
      <img src="http://localhost/++skin++cms/repository/2006/new-hampshire/new-hampshire-450x200.jpg/preview" alt="" height="200" width="450" border="0" />
    </td>
    <td>
      <span class="SearchableText"></span><span class="URL">http://localhost/++skin++cms/repository/2006/new-hampshire/new-hampshire-450x200.jpg</span><span class="uniqueId">http://xml.zeit.de/2006/new-hampshire/new-hampshire-450x200.jpg</span>
    </td>
  </tr>
  <tr class="even">
    ...
    <td>
      new-hampshire-artikel.jpg
    </td>
    <td>
      410x244
    </td>
    <td>
      <img src="http://localhost/++skin++cms/repository/2006/new-hampshire/new-hampshire-artikel.jpg/preview" alt="" height="244" width="410" border="0" />
    </td>
    <td>
      <span class="SearchableText"></span><span class="URL">http://localhost/++skin++cms/repository/2006/new-hampshire/new-hampshire-artikel.jpg</span><span class="uniqueId">http://xml.zeit.de/2006/new-hampshire/new-hampshire-artikel.jpg</span>
    </td>
  </tr>
  <tr class="odd">
    ...
    <td>
      obama-clinton-120x120.jpg
    </td>
    <td>
      120x120
    </td>
    <td>
      <img src="http://localhost/++skin++cms/repository/2006/new-hampshire/obama-clinton-120x120.jpg/preview" alt="" height="120" width="120" border="0" />
    </td>
    <td>
      <span class="SearchableText"></span><span class="URL">http://localhost/++skin++cms/repository/2006/new-hampshire/obama-clinton-120x120.jpg</span><span class="uniqueId">http://xml.zeit.de/2006/new-hampshire/obama-clinton-120x120.jpg</span>
    </td>
  </tr>
  </tbody>
</table>
...

When we want to change the metadata of the image group, we need to check it
out. Checking out an image goup creates a local object (ILocalContent) which is
different from the repository version: it is no folder:

>>> browser.getLink('Checkout').click()
>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.user/new-hampshire/@@edit.html'

>>> print browser.contents
<?xml version="1.0"?>
<!DOCTYPE html ...
    <title> New Hampshire – Edit image group </title>
    ...Objects using this image...


Set the alt text:

>>> browser.getControl('Alternative text').value = 'Wahlkampf'
>>> browser.getControl('Apply').click()


Note that we don't have the view metdata tab on checked out image groups:

>>> browser.getLink('View metadata').click()
Traceback (most recent call last):
    ...
LinkNotFoundError

But an edit tab:

>>> browser.getLink('Edit metadata').click()
>>> print browser.title.strip()
New Hampshire – Edit image group

Make sure we have a metadata preview for local image groups:

>>> browser.open(
...     'http://localhost/++skin++cms/workingcopy/zope.user/'
...     'new-hampshire/@@metadata_preview')
>>> print browser.contents
 <div class="contextViewsAndActions">
<div class="context-views">
    ...
   <div>New Hampshire</div>
    ...

Checkin again:

>>> browser.getLink('Checkin').click()
>>> browser.url
'http://localhost/++skin++cms/repository/2006/new-hampshire/@@view.html'

Check the metadata view, to verify we have actually changed the alt text:

>>> browser.getLink('View metadata').click()
>>> print browser.contents
<?xml version="1.0"?>
<!DOCTYPE html ...
    <title> New Hampshire – Image group metadata </title>
    ...Wahlkampf...


Make sure we have a metadata preview for repository image groups:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/2006/'
...     'new-hampshire/@@metadata_preview')
>>> print browser.contents
 <div class="contextViewsAndActions">
<div class="context-views">
    ...
    <div>New Hampshire</div>
    <div class="image-group-image-preview">
      <img src="http://localhost/++skin++cms/repository/2006/new-hampshire/new-hampshire-450x200.jpg/thumbnail" alt="" height="44" width="100" border="0" />
    </div>
    <div class="image-group-image-preview">
      <img src="http://localhost/++skin++cms/repository/2006/new-hampshire/new-hampshire-artikel.jpg/thumbnail" alt="" height="59" width="100" border="0" />
    </div>
    <div class="image-group-image-preview">
      <img src="http://localhost/++skin++cms/repository/2006/new-hampshire/obama-clinton-120x120.jpg/thumbnail" alt="" height="100" width="100" border="0" />
    </div>
    ...

Make sure the image group view doesn't break when there is some other object
than an image in the image group:

>>> import StringIO
>>> import zope.component
>>> import zeit.connector.interfaces
>>> import zeit.connector.resource
>>> connector = zope.component.getUtility(
...     zeit.connector.interfaces.IConnector)
>>> connector.add(zeit.connector.resource.Resource(
...     'http://xml.zeit.de/2006/new-hampshire/foo',
...     'foo', 'strage-type', StringIO.StringIO('data')))
>>> import transaction
>>> transaction.commit()

>>> browser.open('http://localhost/++skin++cms/repository/2006/new-hampshire')
>>> print browser.contents
<?xml ...
    <td>
      new-hampshire-450x200.jpg
    </td>
    ...

>>> browser.open(
...     'http://localhost/++skin++cms/repository/2006/'
...     'new-hampshire/@@metadata_preview')
>>> print browser.contents
 <div class="contextViewsAndActions">
<div class="context-views">
    ...
   <div>New Hampshire</div>
    ...


The image group has a special drag pane which shows all the images:

>>> browser.open(
...     'http://localhost/++skin++cms/'
...     'repository/2006/new-hampshire/@@drag-pane.html')
>>> print browser.contents
  <img src="http://localhost/++skin++cms/repository/2006/new-hampshire/new-hampshire-450x200.jpg/thumbnail" alt="" height="44" width="100" border="0" />
  <img src="http://localhost/++skin++cms/repository/2006/new-hampshire/new-hampshire-artikel.jpg/thumbnail" alt="" height="59" width="100" border="0" />
  <img src="http://localhost/++skin++cms/repository/2006/new-hampshire/obama-clinton-120x120.jpg/thumbnail" alt="" height="100" width="100" border="0" />
  <div class="Text">New Hampshire</div>
  <div class="UniqueId">http://xml.zeit.de/2006/new-hampshire</div>


It is possible to open the object browser on an image group (this used to
break):

>>> browser.open(
...     'http://localhost/++skin++cms/repository/2006/new-hampshire/'
...     '@@get_object_browser')
>>> print browser.contents
 <h1>http://xml.zeit.de/2006/new-hampshire</h1>
 ...

Image groups also have a thumbnail:

>>> browser.open('@@thumbnail')
>>> print browser.headers
Status: 200 Ok
Content-Length: 2429
Content-Type: image/jpeg
Last-Modified: ...
>>> browser.contents[:16]
'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01'

Broken images
=============

It is not possible to create images with broken data (i.e. PIL must be able to
read it):

>>> browser.open('http://localhost/++skin++cms/repository')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Image (single)']
>>> browser.open(menu.value[0])
>>> test_data = StringIO.StringIO('392-392938r82r')
>>> file_control = browser.getControl(name='form.blob')
>>> file_control.add_file(test_data, 'image/jpeg', 'corrupt.jpg')
>>> browser.getControl(name='form.actions.add').click()
>>> print browser.contents
<?xml ...
    ...The uploaded image could not be identified...



Headers and caching
===================

Images are sent with correct-type, length and last-modified headers:

>>> image.open(
...     'http://localhost/++skin++cms/repository/2006/DSC00109_2.JPG/@@index.html')
>>> print image.headers
Status: 200 Ok
Content-Length: 2926
Content-Type: image/jpeg
Last-Modified: ...
X-Powered-By: Zope (www.zope.org), Python (www.python.org)


An if-modified-since header is also honoured:

>>> import datetime
>>> modified = datetime.datetime.now() + datetime.timedelta(seconds=360)
>>> modified = modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
>>> image.addHeader('If-Modified-Since', modified)
>>> image.open(
...     'http://localhost/++skin++cms/repository/2006/DSC00109_2.JPG/@@index.html')
Traceback (most recent call last):
    ...
HTTPError: HTTP Error 304: Not Modified
>>> print image.headers
Status: 304 Not Modified
Content-Length: 0
Content-Type: image/jpeg
Last-Modified: ...
X-Powered-By: Zope (www.zope.org), Python (www.python.org)


>>> image = zope.testbrowser.testing.Browser()
>>> image.addHeader('Authorization', 'Basic user:userpw')
>>> image.addHeader('If-Modified-Since', 'Fri, 07 Feb 2008 12:47:16 GMT')
>>> image.open(
...     'http://localhost/++skin++cms/repository/2006/DSC00109_2.JPG/@@index.html')
>>> print image.headers
Status: 200 Ok
Content-Length: 2926
Content-Type: image/jpeg
Last-Modified: ...
X-Powered-By: Zope (www.zope.org), Python (www.python.org)
