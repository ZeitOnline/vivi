Portraitbox UI
==============

Create a testbrowser first:

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')


Lets create a portraitbox:

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Portraitbox']
>>> browser.open(menu.value[0])

We are now at the add form. Set the filename:

>>> browser.getControl('File name').value = 'Wurst-Hans'

The infobox has a name and html content:

>>> browser.getControl('First and last name').value = 'Hans Wurst'
>>> browser.getControl('Text').value = '<strong>HW</strong> is in da house'

Reference an image:

>>> browser.getControl('Image').value = (
...     'http://xml.zeit.de/2006/DSC00109_2.jpg')

Finnaly add the portraitbox:

>>> browser.getControl('Add').click()


We're now at the edit form:

>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.user/Wurst-Hans/@@edit.html'

Make sure the box is listed in the workingcopy panel:

>>> print browser.contents
<?xml ...
    <td>
      <a href="http://localhost/++skin++cms/workingcopy/zope.user/Wurst-Hans/edit.html">Hans Wurst</a>
    </td>
    ...


Let's check it in:

>>> browser.handleErrors = False
>>> browser.getLink('Checkin').click()
>>> print browser.contents
<?xml ...
    <title> View portraitbox </title>
    ...


Make sure there is a metadata preview:

>>> browser.url
'http://localhost/++skin++cms/repository/online/2007/01/Wurst-Hans/@@view.html'
>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/'
...     'Wurst-Hans/@@metadata_preview')
>>> print browser.contents
 <div class="contextViewsAndActions">
    <div class="context-views">
    ...
    <div class="title">Hans Wurst</div>
    ...

Make sure an box has a default view:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/Wurst-Hans')
>>> print browser.contents
<?xml ...
    <title> View portraitbox </title>
    ...
