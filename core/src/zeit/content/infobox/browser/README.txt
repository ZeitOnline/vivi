=======
Infobox
=======

Create a testbrowser first:

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')



Lets create an infobox:

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Infobox']
>>> browser.open(menu.value[0])

We are now at the add form. Set the filename:

>>> browser.getControl('File name').value = 'infobox'

The infobox has a super title:

>>> browser.getControl('Supertitle').value = 'Altersvorsorge'

Adding the content text works by clicking the `add contents` button:

>>> browser.getControl('Add Contents').click()
>>> browser.getControl(name='form.contents.0..combination_00').value = (
...     'Renteninformation')
>>> browser.getControl(name='form.contents.0..combination_01').value = (
...    'Nutzen Sie die Renteninformation, um Ihre Versorgungslücke im ')

Finnaly add the infobox:

>>> browser.getControl(name='form.actions.add').click()


We're now at the edit form:

>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.user/infobox/@@edit.html'
>>> browser.getControl(name='form.contents.0..combination_00').value
'Renteninformation'

Make sure the infobox is listed in the workingcopy panel:

>>> print browser.contents
<?xml ...
    <td>
      <a href="http://localhost/++skin++cms/workingcopy/zope.user/infobox/edit.html">Altersvorsorge</a>
    </td>
    ...


Let's add another text entry:

>>> browser.getControl('Add Contents').click()
>>> browser.getControl(name='form.contents.1..combination_00').value = (
...     'Fehlende Versicherungszeiten')
>>> browser.getControl(name='form.contents.1..combination_01').value = (
...     'Pruefen Sie, ob in Ihrer Renteninformation alle ')
>>> browser.getControl('Apply').click()
>>> print browser.contents
<?xml ...
    <title> Edit infobox </title>
    ...Updated on...


Let's check it in:

>>> browser.getLink('Checkin').click()
>>> print browser.contents
<?xml ...
    <title> View infobox </title>
    ...


Make sure there is a metadata preview:

>>> browser.url
'http://localhost/++skin++cms/repository/online/2007/01/infobox/@@view.html'
>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/'
...     'infobox/@@metadata_preview')
>>> print browser.contents
 <div class="contextViewsAndActions">
    <div class="context-views">
    ...
    <div class="title">Altersvorsorge</div>
    </div>

Make sure an infobox has a default view:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/infobox')
>>> print browser.contents
<?xml ...
    <title> View infobox </title>
    ...
