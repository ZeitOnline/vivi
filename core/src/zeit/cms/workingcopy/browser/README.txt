============
Working Copy
============

The working copy is the area of the CMS where users actually edit content.
Create a test browser first:

>>> from z3c.etestbrowser.testing import ExtendedTestBrowser
>>> browser = ExtendedTestBrowser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')


When we access our working copy it is created on the fly if it does not exist
yet. So let's open our workingcopy. It doesn't contain any documents, yet:

>>> browser.open('http://localhost/++skin++cms/workingcopy/zope.user')
>>> print browser.contents
<?xml version...
<!DOCTYPE ...
No edited documents...

 
Adding content to the working copy works by checking them out. Let's view the
repository and checkout a document:

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01/Somalia')
>>> print browser.contents
<?xml version...
<!DOCTYPE ...
...namespaces.zeit.de...
...Terrorismus...
...Jochen Stahnke...

Checkout the Somalia Article:

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01/Somalia/checkout')

Checking out redirected us to the document *in* the working copy:

>>> browser.url
'http://localhost/++skin++cms/workingcopy/zope.user/Somalia/@@view.html'

The sidebar lists the document now:

>>> print browser.contents
<?xml ...
<!DOCTYPE html ...
  <tbody>
  <tr>
    <td>
      <img src="http://localhost/++skin++cms/@@/zeit-cms-repository-interfaces-IUnknownResource-zmi_icon.png" alt="UnknownResource" width="20" height="20" border="0" />
    </td>
    <td>
      <a href="http://localhost/++skin++cms/workingcopy/zope.user/Somalia/edit.html">Somalia</a>
    </td>
    <td>
      <span class="URL">http://localhost/++skin++cms/workingcopy/zope.user/Somalia</span><span class="uniqueId">http://xml.zeit.de/online/2007/01/Somalia</span>
    </td>
  </tr>
  </tbody>
</table>
...


There is a link to get to the original document:

>>> bookmark = browser.url
>>> browser.getLink('Show original')
<Link text='[IMG] Show original' url='http://localhost/++skin++cms/repository/online/2007/01/Somalia/@@view.html'>

There link will not be rendered when the original document was deleted:

>>> browser.getLink('Show original').click()
>>> browser.getLink('Delete').url
"javascript:zeit.cms.lightbox_form('http://localhost/++skin++cms/repository/online/2007/01/Somalia/@@delete.html')"
>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01/Somalia/@@delete.html')
>>> browser.getControl('Delete').click()
>>> browser.open(bookmark)
>>> browser.getLink('Show original')
Traceback (most recent call last):
    ...
LinkNotFoundError

But we can check in the object of couse:

>>> browser.getLink('Checkin').click()

Looking at our working copy also shows the `Somalia` article:

>>> browser.getLink('Checkout').click()
>>> browser.getLink('Edited documents').click()
>>> print browser.contents
<?xml version...
<!DOCTYPE ...
...Somalia...

There is a delete link to remove object from the workingcopy again:

>>> browser.getLink('Somalia').click()
>>> browser.getLink('Cancel')
<Link text='[IMG] Cancel'
    url="javascript:zeit.cms.lightbox_form('http://localhost/++skin++cms/workingcopy/zope.user/Somalia/@@delete.html')">

Let's open the delete form:

>>> browser.open(
...     'http://localhost/++skin++cms/workingcopy/zope.user/Somalia/'
...     '@@delete.html')
>>> print browser.contents
<div class="topcontent deleteScreen">
  <h1>Delete from workingcopy</h1>
  ...
  <p>
    <span>
      Do you really want to delete your workingcopy?
    </span>
  </p>
  <p class="DeleteItem">
    <img src="http://localhost/++skin++cms/@@/zeit-cms-repository-interfaces-IUnknownResource-zmi_icon.png" alt="UnknownResource" width="20" height="20" border="0" />
    <span>Somalia</span>
    (<span>http://xml.zeit.de/online/2007/01/Somalia</span>)
  </p>
  <form action="http://localhost/++skin++cms/workingcopy/zope.user/Somalia/delete.html"...
    <p>
      <input type="submit" value="Delete" name="form.actions.delete" />
    </p>
  </form>
</div>


Let's delete it:

>>> browser.getControl('Delete').click()
>>> print browser.contents
<span class="nextURL">http://localhost/++skin++cms/repository/online/2007/01/Somalia</span>
>>> browser.open('http://localhost/++skin++cms/workingcopy/zope.user')
>>> print browser.contents
<?xml ...
      <div id="topcontent">
        <span class="Info">There are no objects in this folder.</span>
      </div>
      ...

Let's try this again, this time marking an article as renameable, which should
be a property of articles just created. Such articles are to be removed from
the repository when they are deleted explicitly from the working copy:

We need some setup:

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()

>>> import zope.component
>>> import zeit.cms.workingcopy.interfaces
>>> import zeit.cms.browser.interfaces
>>> workingcopy_location = zope.component.getUtility(
...     zeit.cms.workingcopy.interfaces.IWorkingcopyLocation)
>>> workingcopy = workingcopy_location['zope.user']

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01/Querdax')
>>> browser.getLink('Checkout').click()
>>> co = workingcopy.values().next()
>>> import zeit.cms.repository.interfaces
>>> zeit.cms.repository.interfaces.IAutomaticallyRenameable(
...     co).renameable = True
>>> browser.open(
...     'http://localhost/++skin++cms/workingcopy/zope.user/Querdax/@@delete.html')
>>> browser.getControl('Delete').click()
>>> print browser.url
http://localhost/++skin++cms/workingcopy/zope.user/Querdax/delete.html?form.actions.delete=Delete
>>> print browser.contents
<span class="nextURL">http://localhost/++skin++cms/repository/online/2007/01</span>


Sorting
=======

The sidebar is sorted in a way that the document which was checked out last is
the first. Checkout two documents:

>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/Somalia')
>>> browser.getLink('Checkout').click()
>>> browser.open(
...     'http://localhost/++skin++cms/repository/online/2007/01/studiVZ')
>>> browser.getLink('Checkout').click()

>>> print browser.contents
<?xml ...
<!DOCTYPE html ...
  <tbody>
  <tr>
    <td>
      <img src="http://localhost/++skin++cms/@@/zeit-cms-repository-interfaces-IUnknownResource-zmi_icon.png" alt="UnknownResource" width="20" height="20" border="0" />
    </td>
    <td>
      <a href="http://localhost/++skin++cms/workingcopy/zope.user/studiVZ/edit.html">studiVZ</a>
    </td>
    <td>
      <span class="URL">http://localhost/++skin++cms/workingcopy/zope.user/studiVZ</span><span class="uniqueId">http://xml.zeit.de/online/2007/01/studiVZ</span>
    </td>
  </tr>
  <tr>
    <td>
      <img src="http://localhost/++skin++cms/@@/zeit-cms-repository-interfaces-IUnknownResource-zmi_icon.png" alt="UnknownResource" width="20" height="20" border="0" />
    </td>
    <td>
      <a href="http://localhost/++skin++cms/workingcopy/zope.user/Somalia/edit.html">Somalia</a>
    </td>
    <td>
      <span class="URL">http://localhost/++skin++cms/workingcopy/zope.user/Somalia</span><span class="uniqueId">http://xml.zeit.de/online/2007/01/Somalia</span>
    </td>
  </tr>
  </tbody>
</table>
...


Object browser
==============

When the objectbrowser asks for the default location of a content object in the 
working copy, the answer is relayed to the object in the repository.

There is no default location for the working copy itself:

>>> import zeit.cms.content.interfaces
>>> source = zope.component.getUtility(
...     zeit.cms.content.interfaces.ICMSContentSource, name='all-types')
>>> zope.component.getMultiAdapter(
...     (workingcopy, source),
...     zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
Traceback (most recent call last):
    ...
ComponentLookupError:
    ((<zeit.cms.workingcopy.workingcopy.Workingcopy object at 0x...>,
      <zeit.cms.content.contentsource.CMSContentSource object at 0x...>),
     <InterfaceClass zeit.cms.browser.interfaces.IDefaultBrowsingLocation>,
     u'')

For the somalia document we'll get the folder in the repository though:

>>> somalia = workingcopy['Somalia']
>>> location = zope.component.getMultiAdapter(
...     (somalia, source),
...     zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
>>> location.uniqueId
u'http://xml.zeit.de/online/2007/01'


When the object does not exist in the repository we're trying to get the
parent. Let's change the uniquyeId of somalia:

>>> somalia.uniqueId = u'http://xml.zeit.de/online/2009/15'

Getting the location will get us to `online` since that is the nearest existing
folder:

>>> location = zope.component.getMultiAdapter(
...     (somalia, source),
...     zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
>>> location.uniqueId
u'http://xml.zeit.de/online'


Cleanup:

>>> import transaction
>>> transaction.abort()


Preview
=======

Open the checked out somalia and change its source:

>>> browser.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...     'Somalia/@@view.html')
>>> browser.getLink('Source').click()
>>> browser.getControl('Document content').value = 'no more!'
>>> browser.getControl('Apply').click()

When we look at the preview now[#prepare-preview]_:

>>> browser.handleErrors = False
>>> browser.getLink('Preview').click()
>>> print browser.contents
The quick brown fox jumps over the lazy dog.

The preview object will have been be removed though:

>>> browser.open('http://localhost/++skin++cms/repository/online/2007/01')
>>> 'preview-zope.user' in browser.contents
False


Check the preview again to make sure the created folders are used and the
preview doesn't break when the folders already exist:

>>> browser.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...     'Somalia/@@view.html')
>>> browser.getLink('Preview').click()
>>> print browser.contents
The quick brown fox jumps over the lazy dog.

Query arguments are passed to the server:

>>> 
>>> browser.open('http://localhost/++skin++cms/workingcopy/zope.user/'
...     'Somalia/@@view.html')
>>> url = browser.getLink('Preview').url
>>> browser.open(url + '?foo=bar')
>>> print browser.contents
The quick brown foo jumps over the lazy bar.

Clean up:

>>> import shutil
>>> shutil.rmtree(tempdir)


.. [#prepare-preview] We change the preview path to some temp directory and put
    a file there. This will at leas give us some result to verify. 

    >>> import os
    >>> import os.path
    >>> import tempfile
    >>> tempdir = tempfile.mkdtemp()

    Create a preview file. It is created deep in a folder, so create those as
    well:

    >>> preview_dir = os.path.join(tempdir, 'online', '2007', '01')
    >>> os.makedirs(preview_dir)

    >>> name = os.path.join(preview_dir, 'preview-zope.user-Somalia?')
    >>> open(name, 'w').write(
    ...     'The quick brown fox jumps over the lazy dog.')

    Create another file:
    >>> foo_name = name + 'foo=bar'
    >>> file(foo_name, 'w').write(
    ...     'The quick brown foo jumps over the lazy bar.')

    >>> import zope.app.appsetup.product
    >>> cms_config = zope.app.appsetup.product._configs['zeit.cms']

    >>> cms_config['preview-prefix'] = u'file://%s' % tempdir
