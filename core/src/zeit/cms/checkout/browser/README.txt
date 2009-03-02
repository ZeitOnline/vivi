===============================
Checkin/Checkout User-Interface
===============================

Create a browser first:

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')
>>> browser.handleErrors = False


Checkout
========

Checkout is possible for Repository content. Let's open a dockument in the
repository and look at its `metadata_preview` page. We do have a checkout link
but no checkin link:

>>> browser.open('http://localhost/++skin++cms/repository/online/'
...     '2007/01/rauchen-verbessert-die-welt/metadata_preview')
>>> checkout = browser.getLink('Checkout')
>>> checkout
<Link text='[IMG] Checkout...>

The url has information about the view where the link was generated from:

>>> checkout.url
'http://localhost/.../rauchen-verbessert-die-welt/@@checkout?came_from=metadata_preview'

>>> browser.getLink('Checkin')
Traceback (most recent call last):
  ...
LinkNotFoundError


Check the document out by clicking on the link:

>>> checkout.click()
>>> print browser.contents
<?xml version...
<!DOCTYPE ...
    <li class="message">"rauchen-verbessert-die-welt" has been checked out.</li>
    ...
  Unbekannte Resource...


Checkin
=======

After checking out we see the checked out document and can check it in again.
There is of course no checkout button any more:

>>> checkout = browser.getLink('Checkout')
Traceback (most recent call last):
  ...
LinkNotFoundError

The checkin link also indicates the ``came_from`` view:

>>> browser.getLink('Checkin').url
'http://localhost/++skin++cms/workingcopy/zope.user/rauchen-verbessert-die-welt/@@checkin?came_from=view.html'

>>> browser.getLink('Checkin').click()
>>> browser.url
'http://localhost/++skin++cms/repository/online/2007/01/rauchen-verbessert-die-welt/@@view.html'
>>> print browser.contents
<?xml version...
<!DOCTYPE ...
    <li class="message">"rauchen-verbessert-die-welt" has been checked in.</li>
    ...

The "last semantic change" has been set by the check in:

>>> import zope.app.component.hooks
>>> old_site = zope.app.component.hooks.getSite()
>>> zope.app.component.hooks.setSite(getRootFolder())
>>> import zope.component
>>> import zeit.cms.repository.interfaces
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> import zeit.cms.content.interfaces
>>> sc = zeit.cms.content.interfaces.ISemanticChange(
...     repository['online']['2007']['01']['rauchen-verbessert-die-welt'])
>>> last_change = sc.last_semantic_change
>>> last_change
datetime.datetime(...)
>>> zope.app.component.hooks.setSite(old_site)

There is also a checkin action for only minor changes, which does not update
the last semantic change:

>>> browser.getLink('Checkout').click()
>>> browser.getLink('Checkin (correction').click()
>>> import zope.app.component.hooks
>>> old_site = zope.app.component.hooks.getSite()
>>> zope.app.component.hooks.setSite(getRootFolder())
>>> import zope.component
>>> import zeit.cms.repository.interfaces
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> import zeit.cms.content.interfaces
>>> sc = zeit.cms.content.interfaces.ISemanticChange(
...     repository['online']['2007']['01']['rauchen-verbessert-die-welt'])
>>> last_change == sc.last_semantic_change
True
>>> zope.app.component.hooks.setSite(old_site)


Getting the right tab after checkout and checkin
================================================

Checkout and checkin try to redirect to a meaningful view after the
checkout/checkin has happend.

Checkout adapts the context to IEditViewName and uses the resulting view name
as new view.  If there is no adapter, 'edit.html' is used; we've seen this
above.

Register an adapter from 'view.html' to 'foobar.html':

>>> import zope.component
>>> import zeit.cms.browser.interfaces
>>> gsm = zope.component.getGlobalSiteManager()
>>> def view_foobar(context):
...     return 'foobar.html'
>>> gsm.registerAdapter(
...     view_foobar,
...     (zope.interface.Interface,),
...     zeit.cms.browser.interfaces.IEditViewName,
...     name='view.html')


Since the foobar view doesn't actually exist we'll get an error:

>>> browser.open(browser.url)
>>> browser.getLink('Checkout').click()
Traceback (most recent call last):
    ...
NotFound:
    Object: <zeit.cms.repository.unknown.PersistentUnknownResource object at 0x...>,
    name: u'@@foobar.html'

Clean up the adpater:

>>> gsm.unregisterAdapter(
...     view_foobar,
...     (zope.interface.Interface,),
...     zeit.cms.browser.interfaces.IEditViewName,
...     name='view.html')
True


The checkin view adapts the context to IDisplayViewName instead of
IEditViewName.

>>> def edit_foobar(context):
...     return 'foobar.html'
>>> gsm.registerAdapter(
...     edit_foobar,
...     (zope.interface.Interface,),
...     zeit.cms.browser.interfaces.IDisplayViewName,
...     name='view.html')

Open the object checked out before and check it in. Checking in also results in
an error because the foobar view still doesn't exist:

>>> browser.open(
...  'http://localhost/++skin++cms/workingcopy/zope.user/'
...  'rauchen-verbessert-die-welt/@@view.html')
>>> browser.getLink('Checkin').click()
Traceback (most recent call last):
    ...
NotFound:
    Object: <zeit.cms.repository.unknown.PersistentUnknownResource object at 0x...>,
    name: u'@@foobar.html'

Clean up the adapter:

>>> gsm.unregisterAdapter(
...     edit_foobar,
...     (zope.interface.Interface,),
...     zeit.cms.browser.interfaces.IDisplayViewName,
...     name='view.html')
True
