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
     <div id="cp-content">
     </div>
     <div id="cp-forms">
     </div>
 </div>
 ...


The contents of cp-content is loaded via javascript:

>>> browser.open('contents')
>>> bookmark = browser.url
>>> print browser.contents
<div...
<div class="cp-editor-top">
  <div id="cp-aufmacher">
    <div id="cp-aufmacher-inner" class="editable-area validation-error"...
  <div id="cp-informatives">
    <div id="cp-informatives-inner" class="editable-area"...
  <div id="cp-teasermosaic" class="editable-area"
       cms:url="http://localhost/++skin++cms/workingcopy/zope.user/island/teaser-mosaic">...


Add a block in the lead area. This is called by the javascript; the method
returns the URL of the freshly created block:

>>> browser.getLink('Add block').click()
>>> browser.contents
'http://localhost/++skin++cms/workingcopy/zope.user/island/lead/5841f03e-c41b-4239-9ac5-0b19e288cb90'

The block is now contained in the contents:

>>> browser.open(bookmark)
>>> print browser.contents
<div ...
   <div id="cp-aufmacher">...
     <div class="block type-placeholder" cms:url="..." id="<GUID>">...
  <div id="cp-informatives">...
  <div id="cp-teasermosaic"...

We've just created the placeholder block. Its edit view allows us to replace the
contents:

>>> browser.getLink('Click here to choose the block type.').click()
>>> print browser.contents
<div...
   <h1>Choose block type</h1>
   ...
   <div class="block-types">
     <a href="..." cms:cp-module="...LoadAndReload">List of teasers</a>
     ...


The change links is again activated via javascript and returns the URL of the
created object:

>>> browser.getLink('List of teasers').click()
>>> browser.contents
'http://localhost/++skin++cms/workingcopy/zope.user/island/lead/8681a368-ce91-4ae9-b40d-c59fa1dd3640'


The placeholder is gone now and we've got the teaser list:

>>> browser.open(bookmark)
>>> print browser.contents
<div ...
   <div id="cp-aufmacher">...
        <div class="block type-teaser... id="<GUID>">...
  <div id="cp-informatives">...
  <div id="cp-teasermosaic" class="editable-area"...


Sorting
+++++++

Blocks can be sorted. There is an ``updateOrder`` view doing this. Add another
teaser bar:

>>> browser.open(bookmark)
>>> browser.getLink('Add teaser bar').click()
>>> browser.open(bookmark)
>>> browser.getLink('Add teaser bar').click()
>>> browser.open(bookmark)
>>> bar_divs = browser.etree.xpath(
...     '//div[@id="cp-teasermosaic"]/div[contains(@class, "type-teaser-bar")]')
>>> bar_ids = original_ids = [bar.get('id') for bar in bar_divs]
>>> bar_ids
['92ae9ac4-0bd2-4e64-9eeb-40bb10f32f4c',
 'cc243e0c-5814-4180-a336-744ca140c3da']

Reverse the bars:

>>> reversed_ids = tuple(reversed(bar_ids))
>>> import zeit.content.cp.centerpage
>>> zeit.content.cp.centerpage._test_helper_cp_changed = False
>>> import cjson
>>> browser.open(
...     'http://localhost/++skin++cms/workingcopy/zope.user/island/'
...     'teaser-mosaic/updateOrder?keys=' + cjson.encode(reversed_ids))

The order has been updated now:

>>> zeit.content.cp.centerpage._test_helper_cp_changed
True
>>> browser.open(bookmark)
>>> bar_divs = browser.etree.xpath(
...     '//div[@id="cp-teasermosaic"]/div[contains(@class, "type-teaser-bar")]')
>>> bar_ids = tuple(bar.get('id') for bar in bar_divs)
>>> bar_ids == reversed_ids
True

Restore the original order again:

>>> browser.open(
...     'http://localhost/++skin++cms/workingcopy/zope.user/island/'
...     'teaser-mosaic/updateOrder?keys=' + cjson.encode(original_ids))
>>> browser.open(bookmark)
>>> bar_divs = browser.etree.xpath(
...     '//div[@id="cp-teasermosaic"]/div[contains(@class, "type-teaser-bar")]')
>>> bar_ids = tuple(bar.get('id') for bar in bar_divs)
>>> bar_ids == tuple(original_ids)
True


Deleting blocks
+++++++++++++++

Blocks and teaser bars can be removed using the delete link:

>>> browser.open(bookmark)
>>> len(browser.etree.xpath('//div[contains(@class, "leader")]'))
1
>>> browser.getLink('Delete').url
'http://localhost/++skin++cms/workingcopy/zope.user/island/lead/delete?key=<GUID>'
>>> browser.getLink('Delete').click()
>>> browser.etree.xpath('//div[contains(@class, "leader")]')
Traceback (most recent call last):
...
XMLSyntaxError: None
