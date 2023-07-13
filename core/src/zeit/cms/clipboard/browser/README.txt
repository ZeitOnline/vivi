=========
Clipboard
=========

Create a testbrowser:

>>> from zeit.cms.testing import Browser
>>> browser = Browser(layer['wsgi_app'])
>>> browser.login('user', 'userpw')


Tree
====

The clipboard is displayed as a tree. Initially it's empty:

>>> browser.open('http://localhost/++skin++cms/repository')
>>> print(browser.contents)
<?xml version...
<!DOCTYPE ...
  <div class="PanelContent" id="ClipboardPanelContent">
    <div id="clipboardcontents" class="Tree">
    <ul>
      <li class="Root..." uniqueid="">
        <p>
          <a href="...">Clipboard</a>
          <span class="uniqueId">...</span>
          <a title="Remove" class="deleteLink context-action"...>
             <img alt="Delete".../>
             <span class="action-title">Remove</span>
          </a>
        </p>
      </li>
    </ul>
  </div>
...


Open the drag pane of a content ojbect:

>>> ajax = Browser(layer['wsgi_app'])
>>> ajax.login('user', 'userpw')
>>> ajax.open(browser.url + '/online/2007/01/Somalia/@@drag-pane.html')
>>> print(ajax.contents)
<div class="Text">Somalia</div>
<div class="UniqueId">http://xml.zeit.de/online/2007/01/Somalia</div>

We assume, that we drag the pane over the Clipboard:

>>> ajax.handleErrors = False
>>> ajax.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...           'zeit.cms.clipboard.clipboard.Clipboard/@@addContent?'
...           'add_to=&unique_id=http://xml.zeit.de/online/2007/01/Somalia')
>>> print(ajax.contents)
  <ul>
    <li class="Root..." uniqueid="">
    <p>
      <a href="...">Clipboard</a>
      <span class="uniqueId">...</span>
      <a title="Remove" class="deleteLink context-action"...>
         <img alt="Delete" ... />
         <span class="action-title">Remove</span>
      </a>
      </p>
      <ul>
        <li class="NotRoot type-unknown" uniqueid="Somalia">
          <p>
            <a href="http://localhost/++skin++cms/workingcopy/zope.user/zeit.cms.clipboard.clipboard.Clipboard/Somalia">Somalia</a>
            <span class="uniqueId">...Somalia</span>
            <a title="Remove" class="deleteLink context-action"...>
               <img alt="Delete" ... />
               <span class="action-title">Remove</span>
            </a>
          </p>
        </li>
      </ul>
   </li>
 </ul>


Assume we drop the object `Queerdax` on the `Somalia` object. `Querdax` will be
added *after* the previous object:

>>> ajax.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...           'zeit.cms.clipboard.clipboard.Clipboard/@@addContent?'
...           'add_to=Somalia&'
...           'unique_id=http://xml.zeit.de/online/2007/01/Querdax')
>>> print(ajax.contents)
    <ul>
      <li class="Root..." uniqueid="">
        <p>
          <a href="...">Clipboard</a>
          <span class="uniqueId">...</span>
          <a title="Remove" ...
        </p>
        <ul>
          <li class="NotRoot type-unknown" uniqueid="Somalia">
            <p>
              <a href="...Somalia">Somalia</a>
              <span class="uniqueId">...Somalia</span>
              <a title="Remove" ...
            </p>
          </li>
          <li class="NotRoot type-unknown" uniqueid="Querdax">
            <p>
              <a href="...Querdax">Querdax</a>
              <span class="uniqueId">...Querdax</span>
              <a title="Remove" ...
            </p>
          </li>
        </ul>
     </li>
   </ul>


Reload first the page, to get the test in sync with the "ajax":

>>> browser.reload()

Let's click the link in the tree. We'll be redirect to the object's main view:

>>> browser.getLink('Somalia').click()
>>> browser.url
'http://localhost/++skin++cms/repository/online/2007/01/Somalia/@@view.html'


The clipboard link calls the default view of the clipboard entry:

>>> browser.getLink('Somalia', index=1).url
'http://localhost/++skin++cms/workingcopy/zope.user/zeit.cms.clipboard.clipboard.Clipboard/Somalia'

The link in the listing pane, however, refers to @@view of the clipboard entry,
which also redirects to the referenced object.

>>> browser.open('%s/@@view.html' % browser.getLink('Somalia', index=1).url)
>>> browser.url
'http://localhost/++skin++cms/repository/online/2007/01/Somalia/@@view.html'

And there also is an @@edit.html for clipboard entries, which redirects to
the referenced object, too:

>>> browser.open('%s/@@edit.html' % browser.getLink('Somalia', index=1).url)
>>> browser.url
'http://localhost/++skin++cms/repository/online/2007/01/Somalia/@@view.html'

We can also get the unique id from an entry:  XXX why do we need this?

>>> ajax.open(
...     'http://localhost/++skin++cms/workingcopy/zope.user/'
...     'zeit.cms.clipboard.clipboard.Clipboard/Somalia'
...     '/@@ajax.get_unique_id')
>>> print(ajax.contents)
http://xml.zeit.de/online/2007/01/Somalia


Adding Clips
============

Clipboard entries can be categorised into clips. Adding clips works also via
ajax. Fill out the form and check that the controls are there:

>>> browser.getControl(name='title')
<Control name='title' type='text'>
>>> browser.getControl(name='add_clip')
<SubmitControl name='add_clip' type='submit'>


Actually add a clip using our "ajax" browser. The clip is appended as the last
element of the root node:

>>> ajax.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...           'zeit.cms.clipboard.clipboard.Clipboard/@@addContainer?'
...           'title=New+Clip')
>>> print(ajax.contents)
  <ul>
    <li class="Root..." uniqueid="">
      <p>
      <a href="...">Clipboard</a>
      <span class="uniqueId">...</span>
      ...
      <ul>
        <li class="NotRoot..." uniqueid="Somalia">
        <p>
          <a href="...Somalia">Somalia</a>
          <span class="uniqueId">...Somalia</span>
          ...
        </li>
        <li class="NotRoot..." uniqueid="Querdax">
        <p>
          <a href="...Querdax">Querdax</a>
          <span class="uniqueId">...Querdax</span>
          ...
        </li>
        <li action="expand" class="NotRoot..." uniqueid="New Clip">
        <p>
          <a href="...">New Clip</a>
          ...
        </li>
      </ul>
   </li>
 </ul>


Let's add another clip:
  
>>> ajax.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...           'zeit.cms.clipboard.clipboard.Clipboard/@@addContainer?'
...           'title=Second+Clip')
>>> print(ajax.contents)
  <ul>
    <li class="Root..." uniqueid="">
    <p>
      <a href="...">Clipboard</a>
      <span class="uniqueId">...</span>
      ...
      <ul>
        <li class="NotRoot..." uniqueid="Somalia">
          <p>
          <a href="...Somalia">Somalia</a>
          <span class="uniqueId">...Somalia</span>
          ...
        </li>
        <li class="NotRoot..." uniqueid="Querdax">
          <p>
          <a href="...Querdax">Querdax</a>
          <span class="uniqueId">...Querdax</span>
          ...
        </li>
        <li action="expand" class="NotRoot..." uniqueid="New Clip">
        <p>
          <a href="...">New Clip</a>
          ...
        </li>
        <li action="expand" class="NotRoot..." uniqueid="Second Clip">
        <p>
          <a href="...">Second Clip</a>
          ...
        </li>
      </ul>
   </li>
 </ul>



Moving 
======

We can now move things around. This also works via ajax. Move the `Querdax`
to `New Clip`. This moves `Querdax` after `New Clip` since `New Clip` is not
expanded:

>>> ajax.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...           'zeit.cms.clipboard.clipboard.Clipboard/@@moveContent?'
...           'object_path=Querdax&add_to=New%20Clip')
>>> print(ajax.contents)
  <ul>
    <li class="Root..." uniqueid="">
      <p>
      <a href="...">Clipboard</a>
      ...
      <ul>
        <li class="NotRoot..." uniqueid="Somalia">
        <p>
          <a href="...Somalia">Somalia</a>
          ...
        </li>
        <li action="expand" class="NotRoot..." uniqueid="New Clip">
          <p>
          <a href="...">New Clip</a>
          ...
        </li>
        <li class="NotRoot..." uniqueid="Querdax">
          <p>
          <a href="...Querdax">Querdax</a>
          <span class="uniqueId">...Querdax</span>
          ...
        </li>
        <li action="expand" class="NotRoot..." uniqueid="Second Clip">
          <p>
          <a href="...">Second Clip</a>
          ...
        </li>
      </ul>
   </li>
 </ul>


To move `Querdax` *into* `New Clip` it needs to be expanded:

>>> ajax.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...           'zeit.cms.clipboard.clipboard.Clipboard/tree.html/'
...           '@@expandTree?uniqueId=New%20Clip')
>>> print(ajax.contents)
  <ul>
    <li class="Root..." uniqueid="">
      <p>
      <a href="...">Clipboard</a>
      ...
      <ul>
        <li class="NotRoot..." uniqueid="Somalia">
          <p>
          <a href="...Somalia">Somalia</a>
          ...
        </li>
        <li action="collapse" class="NotRoot..." uniqueid="New Clip">
          <p>
          <a href="...">New Clip</a>
          ...
        </li>
        <li class="NotRoot..." uniqueid="Querdax">
          <p>
          <a href="...Querdax">Querdax</a>
          ...
        </li>
        <li action="expand" class="NotRoot..." uniqueid="Second Clip">
          <p>
          <a href="...">Second Clip</a>
          ...
        </li>
      </ul>
   </li>
 </ul>

>>> ajax.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...           'zeit.cms.clipboard.clipboard.Clipboard/@@moveContent?'
...           'object_path=Querdax&add_to=New%20Clip')
>>> print(ajax.contents)
  <ul>
    <li class="Root..." uniqueid="">
      <p>
      <a href="...">Clipboard</a>
      ...
      <ul>
        <li class="NotRoot..." uniqueid="Somalia">
          <p>
          <a href="...Somalia">Somalia</a>
          ...
        </li>
        <li action="collapse" class="NotRoot..." uniqueid="New Clip">
          <p>
          <a href="...">New Clip</a>
          <span class="uniqueId">...</span>
          ...
          <ul>
            <li class="NotRoot..." uniqueid="New Clip/Querdax">
              <p>
              <a href="...Querdax">Querdax</a>
              ...
            </li>
          </ul>  
        </li>
        <li action="expand" class="NotRoot..." uniqueid="Second Clip">
          <p>
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
>>> print(ajax.contents)
  <ul>
    <li class="Root..." uniqueid="">
      <p>
      <a href="...">Clipboard</a>
      ...
      <ul>
        <li class="NotRoot..." uniqueid="Somalia">
          <p>
          <a href="...Somalia">Somalia</a>
          ...
        </li>
        <li action="collapse" class="NotRoot..." uniqueid="New Clip">
          <p>
          <a href="...">New Clip</a>
          ...
          <ul>
            <li class="NotRoot..." uniqueid="New Clip/Querdax">
              <p>
              <a href="...Querdax">Querdax</a>
              ...
            </li>
            <li action="expand" class="NotRoot..."
              uniqueid="New Clip/Second Clip">
              <p>
              <a href="...">Second Clip</a>
              ...
            </li>
          </ul>  
        </li>
      </ul>
   </li>
 </ul>


Removing Clips
==============

Each clipboard entry can be removed.  We use our "ajax" browser and remove
the Querdax entry we've moved into New Clip above:

>>> link = ajax.getLink('Remove', index=3)
>>> link
<Link text='Remove'
   url='http://localhost/++skin++cms/workingcopy/zope.user/zeit.cms.clipboard.clipboard.Clipboard/New%20Clip/Querdax/@@ajax-delete-entry'>

>>> link.click()
>>> print(ajax.contents)
  <ul>
    <li class="Root..." uniqueid="">
      <p>
      <a href="...">Clipboard</a>
      ...
      <ul>
        <li class="NotRoot..." uniqueid="Somalia">
          <p>
          <a href="...Somalia">Somalia</a>
          ...
        </li>
        <li action="collapse" class="NotRoot..." uniqueid="New Clip">
          <p>
          <a href="...">New Clip</a>
          ...
          <ul>
            <li action="expand" class="NotRoot..."
              uniqueid="New Clip/Second Clip">
              <p>
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
>>> print(browser.contents)
<?xml ...
<!DOCTYPE html ...
<table class="contentListing hasMetadata">
    ...
    <td>
      Somalia
    </td>
    <td>
      <span class="filename">Somalia</span>
    ...


The listing can be sorted. There was once a bug when sorting by modified, so
verify this is working:

>>> browser.handleErrors = False
>>> browser.open(browser.url + '?sort_on%3Atokens=modified')

When a referenced object is deleted, the clip will become an "invalid
reference".

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> import zope.component
>>> from zeit.cms.repository.interfaces import IRepository
>>> repository = zope.component.getUtility(IRepository)
>>> import transaction

>>> del repository['online']['2007']['01']['Somalia']
>>> transaction.commit()

Let's have a look at the sidebar:

>>> browser.open('http://localhost/++skin++cms/repository')
>>> print(browser.contents)
<?xml ...
    <div id="clipboardcontents" class="Tree">
  <ul>
      <li class="Root..." uniqueid="">
        ...
  <ul>
      <li class="NotRoot..." uniqueid="Somalia">
        <p>
        <a href="http://localhost/++skin++cms/workingcopy/zope.user/zeit.cms.clipboard.clipboard.Clipboard/Somalia">Somalia</a>
        ...


Renaming clips
++++++++++++++

Clips can be renamed using the rename lightbox:

>>> browser.getLink('Clipboard').click()
>>> browser.open(browser.url + '/New%20Clip')
>>> browser.getLink('Rename')
<Link text='Rename'
  url='javascript:zeit.cms.lightbox_form('http://localhost/++skin++cms/workingcopy/zope.user/zeit.cms.clipboard.clipboard.Clipboard/New%20Clip/@@rename-clip-lightbox')'>
>>> ajax.open(
...     'http://localhost/++skin++cms/workingcopy/zope.user/'
...     'zeit.cms.clipboard.clipboard.Clipboard/New%20Clip/'
...     '@@rename-clip-lightbox')
>>> print(ajax.contents)
<div>
  <h1>Rename</h1>
  ...

When the form loads the current name is filled in:

>>> ajax.getControl('New clip name').value
'New Clip'

Rename "New Clip" to "Wirtschaft clip":

>>> ajax.getControl('New clip name').value = 'Wirtschaft clip'
>>> ajax.getControl('Rename').click() 
>>> 'There were errors' in ajax.contents
False

Reload the whole page and verify the title change:

>>> ajax.open(
...     '/++skin++cms/workingcopy/zope.user/'
...     'zeit.cms.clipboard.clipboard.Clipboard/New%20Clip')
>>> print(ajax.contents)
<?xml ...
<!DOCTYPE ...
  <li class="message">"New Clip" was renamed to "Wirtschaft clip".</li>
  ...
  <ul>
    <li class="Root..." uniqueid="">
      <p>
      <a href="...">Clipboard</a>
      ...
      <ul>
        <li class="NotRoot..." uniqueid="Somalia">
          <p>
          <a href="...Somalia">Somalia</a>
          ...
        </li>
        <li action="collapse" class="NotRoot..." uniqueid="New Clip">
          <p>
          <a href="...">Wirtschaft clip</a>
          ...
          <ul>
            <li action="expand" class="NotRoot..."
              uniqueid="New Clip/Second Clip">
              <p>
              <a href="...">Second Clip</a>
              ...
            </li>
          </ul>  
        </li>
      </ul>
   </li>
 </ul>
 ...

On the clipboard itself there is no rename action:

>>> browser.getLink('Clipboard').click()
>>> 'Rename' in [
...     node.get('title') for node in 
...     browser.xpath('//*[@class="context-actions"]//a')]
False

Deleting clips
++++++++++++++

On the clipboard itself there is now "Delete" link:

>>> browser.getLink('Clipboard').click()
>>> 'Delete' in [
...     node.get('title') for node in 
...     browser.xpath('//*[@class="context-actions"]//a')]
False

Open "New clip", we have a delete link there:

>>> browser.open(browser.url + '/New%20Clip')
>>> link = browser.getLink('Delete')
>>> link
<Link text='Delete' 
    url='http://localhost/++skin++cms/workingcopy/zope.user/zeit.cms.clipboard.clipboard.Clipboard/New%20Clip/@@delete-clip'>
>>> link.click()
>>> print(browser.contents)
<?xml ...
<!DOCTYPE ...
  <li class="message">"Wirtschaft clip" was removed from the clipboard.</li>
  ...
  <ul>
    <li class="Root..." uniqueid="">
      <p>
      <a href="...">Clipboard</a>
      ...
      <ul>
        <li class="NotRoot..." uniqueid="Somalia">
          <p>
          <a href="...Somalia">Somalia</a>
          ...
        </li>
      </ul>
   </li>
 </ul>
 ...


Copying from clipboard
++++++++++++++++++++++

Content can be copied from the clipbard. Go to a folder in the repository:

>>> browser.open('http://localhost/++skin++cms/repository/online')
>>> browser.getLink('Copy from clipboard')
<Link text='Copy from clipboard' url='javascript:zeit.cms.lightbox_form('http://localhost/++skin++cms/repository/online/@@insert_from_clipboard.lightbox')'>

Let's open the lightbox. It shows the clipboard tree:

>>> browser.handleErrors = False
>>> ajax.open('http://localhost/++skin++cms/repository/online'
...           '/@@insert_from_clipboard.lightbox')
>>> print(ajax.contents)
<div>
  <h1>
    Copy content into
    http://xml.zeit.de/online/
  </h1>
  <div id="LightboxClipboard" class="Tree">
  <ul>
      <li class="Root..." uniqueid="">
        <p>
        <a href="http://localhost/++skin++cms/workingcopy/zope.user/zeit.cms.clipboard.clipboard.Clipboard">Clipboard</a>
   ...
  <script type="text/javascript">
    zeit.cms._lightbox_clipboard = new zeit.cms.Clipboard(
      'http://localhost/++skin++cms/workingcopy/zope.user/zeit.cms.clipboard.clipboard.Clipboard', 'http://localhost/++skin++cms/workingcopy/zope.user/zeit.cms.clipboard.clipboard.Clipboard/tree.html', 'LightboxClipboard');
    zeit.cms._lightbox_clipboard_copy = new zeit.cms.CopyFromClipboard(
      zeit.cms._lightbox_clipboard, 'http://localhost/++skin++cms/repository/online/@@copy');
    </script>...

In the javascript the copy-url is passed to javascript:

>>> copy_url = 'http://localhost/++skin++cms/repository/online/@@copy'

When the user chooses an element from his clipboard the copy url is called with
the unique id of the chosen element. Let's copy

>>> unique_id = 'http://xml.zeit.de/online/2007/01'

to online:


>>> browser.open('%s?unique_id=%s' % (copy_url, unique_id))
>>> browser.url
'http://localhost/++skin++cms/repository/online/01'
>>> print(browser.contents)
<?xml ...
        <li class="message">http://xml.zeit.de/online/2007/01 was copied to
        http://xml.zeit.de/online/01/.</li>
        ...
