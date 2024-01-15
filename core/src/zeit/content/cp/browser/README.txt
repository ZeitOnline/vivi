==========
Centerpage
==========

>>> import zeit.cms.testing
>>> browser = zeit.cms.testing.Browser(layer['wsgi_app'])
>>> browser.login('user', 'userpw')
>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01')

>>> menu = browser.getControl(name='add_menu')
>>> menu.displayValue = ['CenterPage']
>>> browser.open(menu.value[0])

>>> browser.getControl('File name').value = 'island'
>>> browser.getControl('Title').value = 'Auf den Spuren der Elfen'
>>> browser.getControl('Ressort').displayValue = ['Reisen']
>>> browser.getControl('CP type').displayValue = ['Themenseite']
>>> browser.getControl('CAP title').value = 'cap cap cap'
>>> browser.getControl(name="form.actions.add").click()

>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.user/island/@@view.html'
>>> print(browser.contents)
<?xml...
<!DOCTYPE...
...Title...Auf den Spuren der Elfen...
...CP type...Themenseite...
...CAP title...cap cap cap...

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
>>> print(browser.contents)
<...
...Title...Auf den Spuren der Elfen...
...CP type...Themenseite...
>>> browser.getLink('View metadata').click()
>>> print(browser.title.strip())
Auf den Spuren der Elfen – View centerpage metadata


Editor
======

The center page editor requires a lot of javascript, so we're only checking a
few views here.

Check the CP out again, and go to the edit view:

>>> browser.getLink('Checkout').click()
>>> browser.getLink('Edit contents').click()
>>> print(browser.title.strip())
Auf den Spuren der Elfen – Edit


The inital page doens't contain much:

>>> print(browser.contents)
<?xml ...
 <div id="content">
     <div id="cp-content">
       <div id="cp-content-inner">
       </div>
     </div>
     <div id="cp-forms">
     </div>
     ...
 </div>
 ...


The contents of cp-content is loaded via javascript:

>>> browser.open('contents')
>>> contents_url = browser.url
>>> print(browser.contents)
<...
  <div ...class="...editable-area..."...id="lead"...
  <div ...class="...editable-area..."...id="informatives"...

Blocks are added via drag and drop from the block library. The library is
explained in detail in library.txt.


Sorting
+++++++

Blocks can be sorted. There is an ``updateOrder`` view doing this.

>>> browser.open(contents_url)
>>> browser.open(
...     'body/lead/@@landing-zone-drop-module?block_type=teaser&order=top')
>>> browser.open(contents_url)
>>> browser.open(
...     'body/lead/@@landing-zone-drop-module?block_type=teaser&order=top')
>>> browser.open(contents_url)
>>> bar_divs = browser.xpath(
...     '//div[@id="lead"]//div[contains(@class, "type-teaser")]')
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
...     'body/lead/updateOrder?keys=' + json.dumps(reversed_ids))

The order has been updated now:

>>> zeit.content.cp.centerpage._test_helper_cp_changed
True
>>> browser.open(contents_url)
>>> bar_divs = browser.xpath(
...     '//div[@id="lead"]//div[contains(@class, "type-teaser")]')
>>> bar_ids = tuple(bar.get('id') for bar in bar_divs)
>>> bar_ids == reversed_ids
True

Restore the original order again:

>>> browser.open(
...     'http://localhost/++skin++cms/workingcopy/zope.user/island/'
...     'body/lead/updateOrder?keys=' + json.dumps(original_ids))
>>> browser.open(contents_url)
>>> bar_divs = browser.xpath(
...     '//div[@id="lead"]//div[contains(@class, "type-teaser")]')
>>> bar_ids = tuple(bar.get('id') for bar in bar_divs)
>>> bar_ids == tuple(original_ids)
True


Deleting blocks
+++++++++++++++

Blocks and teaser bars can be removed using the delete link:

>>> browser.open(contents_url)
>>> len(browser.xpath('//div[contains(@class, "type-cpextra")]'))
2
>>> browser.getLink('Delete', index=5).url
'http://localhost/++skin++cms/workingcopy/zope.user/island/body/feature/informatives/@@delete?key=id-<GUID>'
>>> browser.getLink('Delete', index=5).click()
>>> browser.open(contents_url)
>>> len(browser.xpath('//div[contains(@class, "type-cpextra")]'))
1
