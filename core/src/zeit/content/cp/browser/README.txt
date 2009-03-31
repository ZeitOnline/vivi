==========
Centerpage
==========

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')
>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01')

>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['CenterPage']
>>> browser.open(menu.value[0])

>>> browser.getControl('File name').value = 'island'
>>> browser.getControl('Title').value = 'Auf den Spuren der Elfen'
>>> browser.getControl('Ressort').displayValue = ['Reisen']
>>> browser.getControl('Daily newsletter').selected = True
>>> browser.getControl(name='form.authors.0.').value = 'Hans Sachs'
>>> browser.getControl(name="form.actions.add").click()

>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.user/island/@@view.html'
>>> print browser.contents
<?xml...
<!DOCTYPE...
Title...Auf den Spuren der Elfen...

We can edit the metadata on the edit tab:

>>> browser.getLink('Edit metadata').click()
>>> browser.getControl('Title').value
'Auf den Spuren der Elfen'

The view is only available after checkin:

>>> browser.getLink('View metadata')
Traceback (most recent call last):
    ...
LinkNotFoundError

>>> browser.getLink('Checkin').click()
>>> browser.getLink('View metadata').click()
>>> print browser.title.strip()
island – View centerpage metadata


Editor
======

The center page editor requires a lot of javascript, so we're only checking a
few views here.

Check the CP out again, and go to the edit view:

>>> browser.getLink('Checkout').click()
>>> browser.getLink('Edit contents').click()
>>> print browser.title.strip()
island – Edit center page


The inital page doens't contain much:

>>> print browser.contents
<?xml ...
 <div id="content">
     <div id="cp-content" xmlns:cms="http://namespaces.gocept.com/zeit-cms">
     </div>
     <div id="cp-search-pane">
     </div>
 </div>
 ...


The contents of cp-content is loaded via javascript:

>>> browser.open('editor-contents')
>>> print browser.contents
<table>
  <tbody>
    <tr>
      <td id="cp-aufmacher" class="editable-area">...</td>
      <td id="cp-informatives" class="editable-area">...</td>
    </tr>
    <tr>
      <td colspan="2" id="cp-teasermosaik" class="editable-area">...</td>
    </tr>
  </tbody>
</table>
