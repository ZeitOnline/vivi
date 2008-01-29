=========
Clipboard
=========

Create a testbrowser:

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')


Tree
====

The clipboard is displayed as a tree. Initially it's empty:

>>> browser.open('http://localhost/++skin++cms/repository')
>>> print browser.contents
<?xml version...
<!DOCTYPE ...
  <div class="PanelContent">
    <div id="clipboardcontents" class="Tree">
    <ul>
      <li class="Root" uniqueid="">
        <a href="...">Clipboard</a>
        <span class="URL">...</span>
        <a title="Remove Clip from Clipboard"
           class="DeleteLink"...>Remove</a>
      </li>
    </ul>
  </div>
...


Open the drag pane of the wirtschaft.feed:

>>> ajax = Browser()
>>> ajax.addHeader('Authorization', 'Basic user:userpw')
>>> ajax.open(browser.url + '/wirtschaft.feed/@@drag-pane.html')
>>> print ajax.contents
<div class="Text">Wirtschaft</div>
<div class="UniqueId">http://xml.zeit.de/wirtschaft.feed</div>

We assume, that we drag the pane over the Clipboard:

>>> ajax.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...           'zeit.cms.clipboard.clipboard.Clipboard/@@addContent?'
...           'add_to=&unique_id=http://xml.zeit.de/wirtschaft.feed')
>>> print ajax.contents
  <ul>
    <li class="Root" uniqueid="">
      <a href="...">Clipboard</a>
      <span class="URL">...</span>
      <a title="Remove Clip from Clipboard"
         class="DeleteLink" ...>Remove</a>
      <ul>
        <li class="NotRoot" uniqueid="wirtschaft.feed">
          <a href="http://localhost/++skin++cms/workingcopy/zope.user/zeit.cms.clipboard.clipboard.Clipboard/wirtschaft.feed">Wirtschaft</a>
          <span class="URL">...wirtschaft.feed</span>
          <a title="Remove Clip from Clipboard"
             class="DeleteLink" ...>Remove</a>
        </li>
      </ul>
   </li>
 </ul>


Assume we drop the object `Queerdax` on the wirtschaft.feed. `Querdax` will be
added *before* the feed:

>>> ajax.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...           'zeit.cms.clipboard.clipboard.Clipboard/@@addContent?'
...           'add_to=wirtschaft.feed&'
...           'unique_id=http://xml.zeit.de/online/2007/01/Querdax')
>>> print ajax.contents
    <ul>
      <li class="Root" uniqueid="">
        <a href="...">Clipboard</a>
        <span class="URL">...</span>
        <a title="Remove Clip from Clipboard"
           class="DeleteLink" ...>Remove</a>
        <ul>
          <li class="NotRoot" uniqueid="wirtschaft.feed">
            <a href="...wirtschaft.feed">Wirtschaft</a>
            <span class="URL">...wirtschaft.feed</span>
            <a title="Remove Clip from Clipboard"
               class="DeleteLink" ...>Remove</a>
          </li>
          <li class="NotRoot" uniqueid="Querdax">
            <a href="...Querdax">Querdax</a>
            <span class="URL">...Querdax</span>
            <a title="Remove Clip from Clipboard"
               class="DeleteLink" ...>Remove</a>
          </li>
        </ul>
     </li>
   </ul>


Reload first the page, to get the test in sync with the "ajax":

>>> browser.url
'http://localhost/++skin++cms/repository'
>>> browser.open(browser.url)


Let's click the link in the tree. We'll be redirect to the wirtschaft.feed
view:

>>> browser.getLink('Wirtschaft').click()
>>> browser.url
'http://localhost/++skin++cms/repository/wirtschaft.feed/@@view.html'


The link Wirtschaft calls the default view of the clipboard entry:

>>> browser.getLink('Wirtschaft').url
'http://localhost/++skin++cms/workingcopy/zope.user/zeit.cms.clipboard.clipboard.Clipboard/wirtschaft.feed'

But there is also an @@edit.html for clipboard entries, which also redirects to
the referenced object:

>>> browser.open('%s/@@edit.html' % browser.getLink('Wirtschaft').url)
>>> browser.url
'http://localhost/++skin++cms/repository/wirtschaft.feed/@@view.html'


Adding Clips
============

Clipboard entries can be categorised into clips. Adding clips works also via
ajax. Fill out the form and check that the controls are there:

>>> browser.getControl(name='title')
<Control name='title' type='text'>
>>> browser.getControl(name='add_clip')
<Control name='add_clip' type='button'>


Actually add a clip using our "ajax" browser. The clip is appended as the last
element of the root node:

>>> ajax.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...           'zeit.cms.clipboard.clipboard.Clipboard/@@addContainer?'
...           'title=New+Clip')
>>> print ajax.contents
  <ul>
    <li class="Root" uniqueid="">
      <a href="...">Clipboard</a>
      <span class="URL">...</span>
      <a title="Remove Clip from Clipboard"
         class="DeleteLink" ...>Remove</a>
      <ul>
        <li class="NotRoot" uniqueid="wirtschaft.feed">
          <a href="...wirtschaft.feed">Wirtschaft</a>
          <span class="URL">...wirtschaft.feed</span>
          <a title="Remove Clip from Clipboard"
             class="DeleteLink" ...>Remove</a>
        </li>
        <li class="NotRoot" uniqueid="Querdax">
          <a href="...Querdax">Querdax</a>
          <span class="URL">...Querdax</span>
          <a title="Remove Clip from Clipboard"
             class="DeleteLink" ...>Remove</a>
        </li>
        <li action="expand" class="NotRoot" uniqueid="New Clip">
          <a href="...">New Clip</a>
          <span class="URL">...New%20Clip</span>
          <a title="Remove Clip from Clipboard"
             class="DeleteLink" ...>Remove</a>
        </li>
      </ul>
   </li>
 </ul>


Let's add another clip:
  
>>> ajax.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...           'zeit.cms.clipboard.clipboard.Clipboard/@@addContainer?'
...           'title=Second+Clip')
>>> print ajax.contents
  <ul>
    <li class="Root" uniqueid="">
      <a href="...">Clipboard</a>
      <span class="URL">...</span>
      <a title="Remove Clip from Clipboard"
         class="DeleteLink" ...>Remove</a>
      <ul>
        <li class="NotRoot" uniqueid="wirtschaft.feed">
          <a href="...wirtschaft.feed">Wirtschaft</a>
          <span class="URL">...wirtschaft.feed</span>
          <a title="Remove Clip from Clipboard"
             class="DeleteLink" ...>Remove</a>
        </li>
        <li class="NotRoot" uniqueid="Querdax">
          <a href="...Querdax">Querdax</a>
          <span class="URL">...Querdax</span>
          <a title="Remove Clip from Clipboard"
             class="DeleteLink" ...>Remove</a>
        </li>
        <li action="expand" class="NotRoot" uniqueid="New Clip">
          <a href="...">New Clip</a>
          <span class="URL">...New%20Clip</span>
          <a title="Remove Clip from Clipboard"
             class="DeleteLink" ...>Remove</a>
        </li>
        <li action="expand" class="NotRoot" uniqueid="Second Clip">
          <a href="...">Second Clip</a>
          <span class="URL">...Second%20Clip</span>
          <a title="Remove Clip from Clipboard"
             class="DeleteLink" ...>Remove</a>
        </li>
      </ul>
   </li>
 </ul>


Removing Clips
==============

Each clipboard entry can be removed. We use our "ajax" browser and
remove the last entry:

>>> print ajax.contents
  <ul>
    <li class="Root" uniqueid="">
      <a href="...">Clipboard</a>
      <span class="URL">...</span>
      <a title="Remove Clip from Clipboard"
         class="DeleteLink" ...>Remove</a>
      <ul>
        <li class="NotRoot" uniqueid="wirtschaft.feed">
          <a href="...wirtschaft.feed">Wirtschaft</a>
          <span class="URL">...wirtschaft.feed</span>
          <a title="Remove Clip from Clipboard"
             class="DeleteLink" ...>Remove</a>
        </li>
        <li class="NotRoot" uniqueid="Querdax">
          <a href="...Querdax">Querdax</a>
          <span class="URL">...Querdax</span>
          <a title="Remove Clip from Clipboard"
             class="DeleteLink" ...>Remove</a>
        </li>
        <li action="expand" class="NotRoot" uniqueid="New Clip">
          <a href="...">New Clip</a>
          <span class="URL">...New%20Clip</span>
          <a title="Remove Clip from Clipboard"
             class="DeleteLink" ...>Remove</a>
        </li>
        <li action="expand" class="NotRoot" uniqueid="Second Clip">
          <a href="...">Second Clip</a>
          <span class="URL">...Second%20Clip</span>
          <a title="Remove Clip from Clipboard"
             class="DeleteLink" ...>Remove</a>
        </li>
      </ul>
   </li>
 </ul>
>>> ajax.open('http://localhost/++skin++cms/workingcopy/'
...           'zope.user/zeit.cms.clipboard.clipboard.Clipboard/'
...           'Second%20Clip/@@deletecontent.html')
>>> print ajax.contents
  <ul>
    <li class="Root" uniqueid="">
      <a href="...">Clipboard</a>
      <span class="URL">...</span>
      <a title="Remove Clip from Clipboard"
         class="DeleteLink" ...>Remove</a>
      <ul>
        <li class="NotRoot" uniqueid="wirtschaft.feed">
          <a href="...wirtschaft.feed">Wirtschaft</a>
          <span class="URL">...wirtschaft.feed</span>
          <a title="Remove Clip from Clipboard"
             class="DeleteLink" ...>Remove</a>
        </li>
        <li class="NotRoot" uniqueid="Querdax">
          <a href="...Querdax">Querdax</a>
          <span class="URL">...Querdax</span>
          <a title="Remove Clip from Clipboard"
             class="DeleteLink" ...>Remove</a>
        </li>
        <li action="expand" class="NotRoot" uniqueid="New Clip">
          <a href="...">New Clip</a>
          <span class="URL">...New%20Clip</span>
          <a title="Remove Clip from Clipboard"
             class="DeleteLink" ...>Remove</a>
        </li>
      </ul>
   </li>
 </ul>

Add the removed clip again:

>>> ajax.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...           'zeit.cms.clipboard.clipboard.Clipboard/@@addContainer?'
...           'title=Second+Clip')


Moving 
======

We can now move things around. This also works via ajax. Move the `Querdax`
to `New Clip`. The tree node is currently collapsed so we won't see the
`Querdax` entry after moving:

>>> ajax.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...           'zeit.cms.clipboard.clipboard.Clipboard/@@moveContent?'
...           'object_path=Querdax&add_to=New%20Clip')
>>> print ajax.contents
  <ul>
    <li class="Root" uniqueid="">
      <a href="...">Clipboard</a>
      ...
      <ul>
        <li class="NotRoot" uniqueid="wirtschaft.feed">
          <a href="...wirtschaft.feed">Wirtschaft</a>
          ...
        </li>
        <li action="expand" class="NotRoot" uniqueid="New Clip">
          <a href="...">New Clip</a>
          ...
        </li>
        <li action="expand" class="NotRoot" uniqueid="Second Clip">
          <a href="...">Second Clip</a>
          ...
        </li>
      </ul>
   </li>
 </ul>


Expand the `New Clip` node:

>>> ajax.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...           'zeit.cms.clipboard.clipboard.Clipboard/tree.html/'
...           '@@expandTree?uniqueId=New%20Clip')
>>> print ajax.contents
  <ul>
    <li class="Root" uniqueid="">
      <a href="...">Clipboard</a>
      ...
      <ul>
        <li class="NotRoot" uniqueid="wirtschaft.feed">
          <a href="...wirtschaft.feed">Wirtschaft</a>
          ...
        </li>
        <li action="collapse" class="NotRoot" uniqueid="New Clip">
          <a href="...">New Clip</a>
          <span class="URL">...</span>
          <a title="Remove Clip from Clipboard"
             class="DeleteLink" ...>Remove</a>
          <ul>
            <li class="NotRoot" uniqueid="New Clip/Querdax">
              <a href="...Querdax">Querdax</a>
              ...
            </li>
          </ul>  
        </li>
        <li action="expand" class="NotRoot" uniqueid="Second Clip">
          <a href="...">Second Clip</a>
          ...
        </li>
      </ul>
   </li>
 </ul>


We can of course also move clips into clips:

>>> ajax.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...           'zeit.cms.clipboard.clipboard.Clipboard/@@moveContent?'
...           'object_path=Second%20Clip&add_to=New%20Clip/Querdax')
>>> print ajax.contents
  <ul>
    <li class="Root" uniqueid="">
      <a href="...">Clipboard</a>
      ...
      <ul>
        <li class="NotRoot" uniqueid="wirtschaft.feed">
          <a href="...wirtschaft.feed">Wirtschaft</a>
          ...
        </li>
        <li action="collapse" class="NotRoot" uniqueid="New Clip">
          <a href="...">New Clip</a>
          ...
          <ul>
            <li class="NotRoot" uniqueid="New Clip/Querdax">
              <a href="...Querdax">Querdax</a>
              ...
            </li>
            <li action="expand" class="NotRoot"
              uniqueid="New Clip/Second Clip">
              <a href="...">Second Clip</a>
              ...
            </li>
          </ul>  
        </li>
      </ul>
   </li>
 </ul>



Clipboard Listing
=================

When accessing the clipboard we get a normal content listing. The feed we have
in the clipboard also has its icon:

>>> browser.getLink('Clipboard').click()
>>> print browser.contents
<?xml ...
<!DOCTYPE html ...
<table class="contentListing hasMetadata">
    ...
    <td>
      <img src="http://localhost/++skin++cms/@@/zeit-cms-syndication-interfaces-IFeed-zmi_icon.png" alt="Feed" width="20" height="20" border="0" />
    </td>
    ...

