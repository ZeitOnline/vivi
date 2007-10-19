=====
Image
=====

Create a browser first:

>>> from z3c.etestbrowser.testing import ExtendedTestBrowser
>>> browser = ExtendedTestBrowser()
>>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')

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
    <div class="heading">
      ...
      <h2>
        ...
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
>>> image.addHeader('Authorization', 'Basic mgr:mgrpw')
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
>>> test_file = os.path.join(os.path.dirname(__file__), 'opernball.jpg')
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

>>> image.open('http://localhost/++skin++cms/workingcopy/zope.mgr/'
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
    <div class="heading">...
    <h2>...
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
>>> 'There where errors' not in browser.contents
True

Make sure the image is not changed by looking at the image view:

>>> browser.getLink('Anzeigen').click()
>>> print browser.contents
<?xml ...
  <h1>
    Opernball in Wien
  </h1>
  ...
  <tr>
    <td>Dimensionen</td>
    <td>
      119x160
    </td>
  </tr>
  ...
