Raw XML browser access
======================

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')

>>> browser.open('http://localhost/++skin++cms')

Add a raw xml:

>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['Raw XML']
>>> url = menu.value[0]
>>> browser.open(menu.value[0])
>>> print browser.contents
<?xml ...
    <title>... Add Raw XML </title>
    ...
>>> browser.getControl('File name').value = 'rawxml'
>>> browser.getControl('Title').value = 'This is raw feed foo'
>>> browser.getControl('XML').value = '<block><feed/></block>'
>>> browser.getControl('Omit root').selected = True
>>> browser.getControl("Add").click()

We're now at the edit page:

>>> print browser.contents
<?xml ...
    <title>... Edit Raw XML </title>
    ...

The xml is pretty printed:

>>> print browser.getControl('XML').value
<block>
  <feed/>
</block>

There is an edit tab:

>>> browser.getLink('Edit', index=1)
<Link text='Edit' url='http://localhost/++skin++cms/workingcopy/zope.user/rawxml/@@edit.html'>


TODO
- Title in list representation
- Checkin / display form


