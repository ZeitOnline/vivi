=============
Image Gallery
=============

Galleries are basically a document which references a folder containing images.
Create a  browser first:

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')


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
>>> browser.getControl('Image folder').value = (
...     'http://xml.zeit.de/online/2007/01/gallery')

#>>> browser.handleErrors = False
#>>> browser.getControl(name="form.actions.add").click()
#>>> browser.url
