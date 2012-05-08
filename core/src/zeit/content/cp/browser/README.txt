==========
Centerpage
==========

>>> import z3c.etestbrowser.testing
>>> browser = z3c.etestbrowser.testing.ExtendedTestBrowser()
>>> browser.xml_strict = True
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
>>> browser.getControl('CP type').displayOptions
['Archiv-Print-Volume', 'Archiv-Print-Year', 'Centerpage', 'Homepage', 'Themenseite']
>>> browser.getControl('CP type').displayValue = ['Themenseite']
>>> browser.getControl('Header image').value = 'http://xml.zeit.de/2006/DSC00109_2.JPG'
>>> browser.getControl('CAP title').value = 'cap cap cap'
>>> browser.getControl(name="form.actions.add").click()

>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.user/island/@@view.html'
>>> print browser.contents
<?xml...
<!DOCTYPE...
...Title...Auf den Spuren der Elfen...
...CAP title...cap cap cap...
...CP type...Themenseite...
...Header image...DSC00109_2.JPG...

There is an asset tab:

>>> browser.getLink('Edit assets').click()
>>> print browser.title.strip()
Auf den Spuren der Elfen – Edit assets

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
>>> print browser.contents
<...
...Title...Auf den Spuren der Elfen...
...CP type...Themenseite...
...Header image...DSC00109_2.JPG...
>>> browser.getLink('View metadata').click()
>>> print browser.title.strip()
Auf den Spuren der Elfen – View centerpage metadata


Editor
======

The center page editor requires a lot of javascript, so we're only checking a
few views here.

Check the CP out again, and go to the edit view:

>>> browser.getLink('Checkout').click()
>>> browser.getLink('Edit contents').click()
>>> print browser.title.strip()
Auf den Spuren der Elfen – Edit centerpage


The inital page doens't contain much:

>>> print browser.contents
<?xml ...
 <div id="content">
     <div id="cp-content">
     </div>
     <div id="cp-forms">
     </div>
     ...
 </div>
 ...


The contents of cp-content is loaded via javascript:

>>> browser.open('contents')
>>> contents_url = browser.url
>>> print browser.contents
<div...
<div class="cp-editor-top">
  <div id="lead-outer"><div id="lead"...class="editable-area validation-error"...
  <div id="informatives-outer"><div id="informatives"...class="editable-area"...
  <div id="teaser-mosaic"...class="editable-area"...


There is a "add block" link which only activates a tab:

>>> browser.getLink('Add block')
<Link text='+ Add block' url='tab://library-informatives'>

Blocks are added via drag and drop from the block library. The library is
explained in detail in library.txt.


Sorting
+++++++

Blocks can be sorted. There is an ``updateOrder`` view doing this. Add another
teaser bar:

>>> browser.open(contents_url)
>>> browser.getLink('Add teaser bar').click()
>>> browser.open(contents_url)
>>> browser.getLink('Add teaser bar').click()
>>> browser.open(contents_url)
>>> bar_divs = browser.etree.xpath(
...     '//div[@id="teaser-mosaic"]/div[contains(@class, "type-teaser-bar")]')
>>> bar_ids = original_ids = [bar.get('id') for bar in bar_divs]
>>> bar_ids
['id-92ae9ac4-0bd2-4e64-9eeb-40bb10f32f4c',
 'id-cc243e0c-5814-4180-a336-744ca140c3da']

Reverse the bars:

>>> import json
>>> import zeit.content.cp.centerpage
>>> reversed_ids = tuple(reversed(bar_ids))
>>> zeit.content.cp.centerpage._test_helper_cp_changed = False
>>> browser.open(
...     'http://localhost/++skin++cms/workingcopy/zope.user/island/'
...     'teaser-mosaic/updateOrder?keys=' + json.dumps(reversed_ids))

The order has been updated now:

>>> zeit.content.cp.centerpage._test_helper_cp_changed
True
>>> browser.open(contents_url)
>>> bar_divs = browser.etree.xpath(
...     '//div[@id="teaser-mosaic"]/div[contains(@class, "type-teaser-bar")]')
>>> bar_ids = tuple(bar.get('id') for bar in bar_divs)
>>> bar_ids == reversed_ids
True

Restore the original order again:

>>> browser.open(
...     'http://localhost/++skin++cms/workingcopy/zope.user/island/'
...     'teaser-mosaic/updateOrder?keys=' + json.dumps(original_ids))
>>> browser.open(contents_url)
>>> bar_divs = browser.etree.xpath(
...     '//div[@id="teaser-mosaic"]/div[contains(@class, "type-teaser-bar")]')
>>> bar_ids = tuple(bar.get('id') for bar in bar_divs)
>>> bar_ids == tuple(original_ids)
True


Deleting blocks
+++++++++++++++

Blocks and teaser bars can be removed using the delete link:

>>> browser.open(contents_url)
>>> len(browser.etree.xpath('//div[contains(@class, "type-cpextra")]'))
2
>>> browser.getLink('Delete').url
'http://localhost/++skin++cms/workingcopy/zope.user/island/informatives/delete?key=id-<GUID>'
>>> browser.getLink('Delete').click()
>>> browser.open(contents_url)
>>> len(browser.etree.xpath('//div[contains(@class, "type-cpextra")]'))
1
