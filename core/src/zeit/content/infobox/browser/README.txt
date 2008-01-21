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

