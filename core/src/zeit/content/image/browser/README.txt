=====
Image
=====

Create a browser first:

>>> from z3c.etestbrowser.testing import ExtendedTestBrowser
>>> browser = ExtendedTestBrowser()
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

>>> image = ExtendedTestBrowser()
>>> image.addHeader('Authorization', 'Basic user:userpw')
>>> image.open(
...     'http://localhost/++skin++cms/repository/2006/DSC00109_2.JPG')
>>> image.headers['content-type']
'image/jpeg'
>>> image.contents[:16]
'\xff\xd8\xff\xe1\x0c\xdaExif\x00\x00MM\x00*'

We also have a preview version of an images. The preview is scaled down on the
server:

>>> image.open('http://localhost/++skin++cms/repository/'
...            '2006/DSC00109_2.JPG/preview')
>>> image.headers['content-type']
'image/jpeg'

And a thumbnail is also scaled on the server:

>>> image.open('http://localhost/++skin++cms/repository/'
...            '2006/DSC00109_2.JPG/thumbnail')
>>> image.headers['content-type']
'image/jpeg'


Editing
=======

For editing an image, we need to check it out:

>>> browser.getLink('Checkout').click()

We now see the form and fill out some values:

>>> import os
>>> test_file = os.path.join(
...     os.path.dirname(__file__), 'testdata', 'opernball.jpg')
>>> test_data = file(test_file, 'rb')
>>> file_control = browser.getControl(name='form.data')
>>> file_control.filename = 'opernball.jpg'
>>> file_control.value = test_data
>>> browser.getControl(name='form.title').value = 'Opernball'
>>> browser.getControl(name='form.year').value = '2007'
>>> browser.getControl(name='form.volume').value = '9'
>>> browser.getControl(name='form.alt').value = 'Zwei Taenzer'
>>> browser.getControl(name='form.caption').value = 'Tanz beim Opernball'
>>> browser.getControl('Apply').click()
>>> 'There where errors' not in browser.contents
True

Verify some values:

>>> browser.getControl(name='form.title').value
'Opernball'
>>> browser.getControl(name='form.year').value
'2007'

Let's verify get the right file data back from the image:

>>> image.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...            'DSC00109_2.JPG')
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
>>> 'There where errors' in browser.contents
False

Make sure the image is not changed by looking at the image view:

>>> browser.getLink('Anzeigen').click()
>>> print browser.contents
<?xml ...
  <title>
    Opernball in Wien
  </title>
  ...
  <tr>
    <td>Dimensionen</td>
    <td>
      119x160
    </td>
  </tr>
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

Load the opernball image data an add w/o setting a file name. This selects the
filename automatically:

>>> file_control = browser.getControl(name='form.data')
>>> file_control.filename = 'opernball.jpg'
>>> file_control.value = file(test_file, 'rb')
>>> browser.getControl(name='form.volume').value != '0'
True
>>> browser.getControl('Add').click()
>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.user/opernball.jpg/@@edit.html'



Image browser
=============

The zeit.content.image package provides an image browser for IFolder:

>>> browser.open('http://localhost/++skin++cms/repository/2006/')
>>> browser.getLink('Bilder').click()
>>> print browser.contents
<?xml version="1.0"?>
<!DOCTYPE html ...
    <title> Images </title>
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
>>> menu.displayValue = ['Image Group']
>>> url = menu.value[0]
>>> browser.open(menu.value[0])
>>> print browser.contents
<?xml version="1.0"?>
<!DOCTYPE html ...
    <title> Add image group </title>
    ...

>>> browser.getControl("File name").value = 'new-hampshire'
>>> browser.getControl('Bildtitel').value = 'New Hampshire'
>>> browser.handleErrors = False
>>> browser.getControl("Add").click()

Image groups are not checked out by default, because adding new images will be
done directly in the repository:

>>> browser.url
'http://localhost/++skin++cms/repository/2006/new-hampshire/@@view.html'
>>> print browser.contents
<?xml version="1.0"?>
<!DOCTYPE html ...
    <title> Image group </title>
    ...


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
...     file_control = browser.getControl(name='form.data')
...     file_control.filename = name
...     file_control.value = test_data

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
    <title> Image group </title>
    ...
  <tbody>
  <tr class="odd">
    <td>
      <input class="hiddenType" id="selection_column.bmV3LWhhbXBzaGlyZS00NTB4MjAwLmpwZw==..used" name="selection_column.bmV3LWhhbXBzaGlyZS00NTB4MjAwLmpwZw==..used" type="hidden" value="" /> <input class="checkboxType" id="selection_column.bmV3LWhhbXBzaGlyZS00NTB4MjAwLmpwZw==." name="selection_column.bmV3LWhhbXBzaGlyZS00NTB4MjAwLmpwZw==." type="checkbox" value="on"  />
    </td>
    <td>
    </td>
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
    <td>
      <input class="hiddenType" id="selection_column.bmV3LWhhbXBzaGlyZS1hcnRpa2VsLmpwZw==..used" name="selection_column.bmV3LWhhbXBzaGlyZS1hcnRpa2VsLmpwZw==..used" type="hidden" value="" /> <input class="checkboxType" id="selection_column.bmV3LWhhbXBzaGlyZS1hcnRpa2VsLmpwZw==." name="selection_column.bmV3LWhhbXBzaGlyZS1hcnRpa2VsLmpwZw==." type="checkbox" value="on"  />
    </td>
    <td>
    </td>
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
    <td>
      <input class="hiddenType" id="selection_column.b2JhbWEtY2xpbnRvbi0xMjB4MTIwLmpwZw==..used" name="selection_column.b2JhbWEtY2xpbnRvbi0xMjB4MTIwLmpwZw==..used" type="hidden" value="" /> <input class="checkboxType" id="selection_column.b2JhbWEtY2xpbnRvbi0xMjB4MTIwLmpwZw==." name="selection_column.b2JhbWEtY2xpbnRvbi0xMjB4MTIwLmpwZw==." type="checkbox" value="on"  />
    </td>
    <td>
    </td>
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
'http://localhost/++skin++cms/workingcopy/zope.user/LocalImageGroup/@@edit.html'

>>> print browser.contents
<?xml version="1.0"?>
<!DOCTYPE html ...
    <title> Edit image group </title>
    ...

Set the alt text:

>>> browser.getControl('ALT-Text').value = 'Wahlkampf'
>>> browser.getControl('Apply').click()

Make sure we have a metadata preview for local image groups:

>>> browser.open(
...     'http://localhost/++skin++cms/workingcopy/zope.user/'
...     'LocalImageGroup/@@metadata_preview')
>>> print browser.contents
<div class="context-views">
    ...
   <div>New Hampshire</div>
 </div>

Checkin again:

>>> browser.getLink('Checkin').click()
>>> browser.url
'http://localhost/++skin++cms/repository/2006/new-hampshire/@@view.html'

Check the metadata view, to verify we have actually changed the alt text:

>>> browser.getLink('Metadata').click()
>>> print browser.contents
<?xml version="1.0"?>
<!DOCTYPE html ...
    <title> Image group metadata </title>
    ...Wahlkampf...


Make sure we have a metadata preview for repository image groups:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/2006/'
...     'new-hampshire/@@metadata_preview')
>>> print browser.contents
<div class="context-views">
    ...
   <div>New Hampshire</div>
 </div>
