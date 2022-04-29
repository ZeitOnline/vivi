===============================
Checkin/Checkout User-Interface
===============================

Create a browser first:

>>> from zeit.cms.testing import Browser
>>> browser = Browser(layer['wsgi_app'])
>>> browser.login('user', 'userpw')


Checkout
========

Checkout is possible for Repository content. Let's open a dockument in the
repository and look at its `metadata_preview` page. We do have a checkout link
but no checkin link:

>>> browser.open('http://localhost/++skin++cms/repository/online/'
...     '2007/01/rauchen-verbessert-die-welt/metadata_preview')
>>> checkout = browser.getLink('Checkout')
>>> checkout
<Link text='Checkout...>

The url has information about the view where the link was generated from:

>>> checkout.url
'http://localhost/.../rauchen-verbessert-die-welt/@@checkout?came_from=metadata_preview'

>>> browser.getLink('Checkin')
Traceback (most recent call last):
  ...
LinkNotFoundError


Check the document out by clicking on the link:

>>> checkout.click()
>>> print(browser.contents)
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
'http://localhost/++skin++cms/workingcopy/zope.user/rauchen-verbessert-die-welt/@@checkin?came_from=view.html&semantic_change=None'

>>> browser.getLink('Checkin').click()
>>> browser.url
'http://localhost/++skin++cms/repository/online/2007/01/rauchen-verbessert-die-welt/@@view.html'
>>> print(browser.contents)
<?xml version...
<!DOCTYPE ...
    <li class="message">"rauchen-verbessert-die-welt" has been checked in.</li>
    ...

The checkin default action does not update the "last semantic change" setting:

>>> import zeit.cms.content.interfaces
>>> import zeit.cms.repository.interfaces
>>> import zeit.cms.testing
>>> import zope.component
>>> zeit.cms.testing.set_site()
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> sc = zeit.cms.content.interfaces.ISemanticChange(
...     repository['online']['2007']['01']['rauchen-verbessert-die-welt'])
>>> last_change = sc.last_semantic_change
>>> print(last_change)
None


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
>>> browser.handleErrors = False
>>> import traceback
>>> try:
...     browser.getLink('Checkout').click()
... except Exception:
...    tb = traceback.format_exc()
... else:
...    tb = ''
>>> print(tb)
Traceback (most recent call last):
...Object: <zeit.cms.repository.unknown.PersistentUnknownResource...>,
   name: '@@foobar.html'

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
>>> try:
...    browser.getLink('Checkin').click()
... except Exception:
...    tb = traceback.format_exc()
... else:
...    tb = ''
>>> print(tb)
Traceback (most recent call last):
...Object: <zeit.cms.repository.unknown.PersistentUnknownResource...>,
   name: '@@foobar.html'

Clean up the adapter:

>>> gsm.unregisterAdapter(
...     edit_foobar,
...     (zope.interface.Interface,),
...     zeit.cms.browser.interfaces.IDisplayViewName,
...     name='view.html')
True
>>> browser.handleErrors = True

Faking redirects
================

For javascript, we provide a variant that does not redirect but instead returns
the URL. It also does not do any view calculation but returns the base URL of
the freshly checked-out/-in object:

>>> browser.open('http://localhost/++skin++cms/repository/online/'
...     '2007/01/Somalia/@@checkout?redirect=False')
>>> url = browser.contents
>>> url
'http://localhost/++skin++cms/workingcopy/zope.user/Somalia'

>>> browser.open(url + '/@@checkin?redirect=False&event=')
>>> browser.contents
'http://localhost/++skin++cms/repository/online/2007/01/Somalia'


Checking out already checked-out objects
========================================

Instead of throwing an error, the @@checkout view just redirects to the already
checked-out object:

>>> browser.open('http://localhost/++skin++cms/repository/online/'
...     '2007/01/Somalia/@@checkout')
>>> browser.open('http://localhost/++skin++cms/repository/online/'
...     '2007/01/Somalia/@@checkout')
>>> print(browser.url)
http://localhost/++skin++cms/workingcopy/zope.user/Somalia/@@view.html
