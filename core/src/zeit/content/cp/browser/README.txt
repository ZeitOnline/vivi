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

>>> browser.open('contents')
>>> bookmark = browser.url
>>> print browser.contents
<div class="cp-editor-top">
  <div id="cp-aufmacher">
    <div class="editable-area">...
  <div id="cp-informatives">
    <div class="editable-area">...
  <div id="cp-teasermosaic" class="editable-area">...


Add a box in the lead area. This is called by the javascript; the method
returns the URL of the freshly created box:

>>> browser.getLink('Add box').click()
>>> browser.contents
'http://localhost/++skin++cms/workingcopy/zope.user/island/lead/5841f03e-c41b-4239-9ac5-0b19e288cb90'

The box is now contained in the contents:

>>> browser.open(bookmark)
>>> print browser.contents
<div ...
   <div id="cp-aufmacher">...
    <div class="editable-area">...
     <div class="box type-placeholder">...
  <div id="cp-informatives">
    <div class="editable-area">...
  <div id="cp-teasermosaic" class="editable-area">...

We've just created the placeholder box. Its edit view allows us to replace the
contents:

>>> browser.getLink('Click here to choose the box type.').click()
>>> print browser.contents
<div...
   <h1>Choose box type</h1>
   ...
   <div class="box-types">
     <a href="..." cms:cp-module="LoadAndReload">List of teasers</a>
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
    <div class="editable-area">...
        <div class="box type-teaser">...
  <div id="cp-informatives">
    <div class="editable-area">...
  <div id="cp-teasermosaic" class="editable-area">...


Teaser mosaic
+++++++++++++

In the teaser mosaic contains teaser bars, add one. It is prefilled with four
placeholders:

>>> browser.getLink('Add teaser bar').click()
>>> browser.open(bookmark)
>>> print browser.contents
<div ...
   <div id="cp-aufmacher">...
    <div class="editable-area">...
        <div class="box type-teaser">...
  <div id="cp-informatives">
    <div class="editable-area">...
  <div id="cp-teasermosaic" class="editable-area">...
      ...
      <div class="box type-placeholder">
      ...
      <div class="box type-placeholder">
      ...
      <div class="box type-placeholder">
      ...
      <div class="box type-placeholder">
      ...
        <div class="edit">
          <a cms:cp-module="LoadAndReload"
             href="http://localhost/++skin++cms/workingcopy/zope.user/island/teaser-mosaic/add?type=teaser-bar">
            + Add teaser bar
          </a>
        </div>
        ...


Deleting boxes
++++++++++++++

Boxes and teaser bars can be removed using the delete link:

>>> browser.getLink('Delete').url
'http://localhost/++skin++cms/workingcopy/zope.user/island/lead/<GUID>/delete'
>>> browser.getLink('Delete').click()

Remove the teaser bar:

>>> browser.open(bookmark)
>>> browser.getLink('Delete').url
'http://localhost/++skin++cms/workingcopy/zope.user/island/teaser-mosaic/<GUID>/delete'
>>> browser.getLink('Delete').click()

Nothing left to delete now:

>>> browser.open(bookmark)
>>> browser.getLink('Delete')
Traceback (most recent call last):
    ...
LinkNotFoundError

