=======
Authors
=======

>>> import zope.testbrowser.testing
>>> browser = zope.testbrowser.testing.Browser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')
>>> browser.open('http://localhost/++skin++vivi/repository/online/2007/01')
>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Author']
>>> browser.open(menu.value[0])
>>> browser.getControl('File name').value = 'william_shakespeare'
>>> browser.getControl('Firstname').value = 'William'
>>> browser.getControl('Lastname').value = 'Shakespeare'
>>> browser.getControl('Email address').value = 'wil.i.am@shakespeare.name'
>>> browser.getControl('Status').displayValue = ['Print']
>>> browser.getControl('VG-Wort ID').value = '12345'
>>> browser.getControl(name='form.actions.add').click()
>>> browser.getLink('Checkin').click()
>>> print browser.contents
<...
    <label for="form.firstname">...
    <div class="widget">William</div>...
    <label for="form.lastname">...
    <div class="widget">Shakespeare</div>...
    <label for="form.vgwortid">...
    <div class="widget">12345</div>...
...

>>> browser.getLink('Checkout').click()
>>> browser.getControl('VG-Wort ID').value = 'flub'
>>> browser.getControl('Apply').click()
>>> print browser.contents
<...Invalid integer data...


Context-free AddForm
====================

Authors provide an add form that can be called from anywhere (without a folder
context), that places the resulting author objects in the folder
``/<authors>/<X>/Firstname_Lastname/index`` where authors is a configurable
path and X the first character of the lastname (uppercased).

>>> browser.open(
...     'http://localhost/++skin++vivi/@@zeit.content.author.add_contextfree')
>>> browser.getControl('File name')
Traceback (most recent call last):
LookupError: label 'File name'
>>> browser.getControl('Firstname').value = 'William'
>>> browser.getControl('Lastname').value = 'Shakespeare'
>>> browser.getControl('VG-Wort ID').value = '12345'
>>> browser.getControl('Status').displayValue = ['Print']
>>> browser.getControl(name='form.actions.add').click()
>>> print browser.contents
<...
     <span class="result">http://xml.zeit.de/foo/bar/authors/S/William_Shakespeare/index</span>
...
>>> browser.open('http://localhost/++skin++vivi/repository/foo/bar/authors/S/William_Shakespeare/index')
>>> print browser.contents
<...
    <label for="form.firstname">...
    <div class="widget">William</div>...
    <label for="form.lastname">...
    <div class="widget">Shakespeare</div>...
    <label for="form.vgwortid">...
    <div class="widget">12345</div>...
...

Adding the same name again creates a different folder:

>>> browser.open(
...     'http://localhost/++skin++vivi/@@zeit.content.author.add_contextfree')
>>> browser.getControl('Firstname').value = 'William'
>>> browser.getControl('Lastname').value = 'Shakespeare'
>>> browser.getControl('VG-Wort ID').value = '9876'
>>> browser.getControl('Status').displayValue = ['Print']
>>> browser.getControl(name='form.actions.add').click()
>>> print browser.contents
<...
     <span class="result">http://xml.zeit.de/foo/bar/authors/S/William_Shakespeare-2/index</span>
...
>>> browser.open('http://localhost/++skin++vivi/repository/foo/bar/authors/S/William_Shakespeare-2/index')
>>> print browser.contents
<...
    <label for="form.firstname">...
    <div class="widget">William</div>...
    <label for="form.lastname">...
    <div class="widget">Shakespeare</div>...
    <label for="form.vgwortid">...
    <div class="widget">9876</div>...
...


Folder listing:

>>> browser.open('http://localhost/++skin++vivi/repository/foo/bar/authors/S/William_Shakespeare-2/')
>>> print browser.contents
<...
    <td>
      William Shakespeare
    </td>
    ...

Using authors
=============

This is mostly a smoke-test that security is set up properly.

>>> browser.open('http://localhost/++skin++vivi/repository/testcontent')
>>> browser.getLink('Checkout').click()
>>> browser.getControl('Add Authors', index=0).click()

XXX disabled until the fields are available again.
# >>> browser.getControl(name='form.author_references.0.').value = (
# ...     'http://xml.zeit.de/foo/bar/authors/S/William_Shakespeare-2/index')
>>> browser.getControl('Apply').click()
>>> browser.getLink('Checkin').click()
>>> print browser.contents
<..."testcontent" has been checked in...
