===============================
Checkin/Checkout User-Interface
===============================

Create a browser first:

>>> from zope.testbrowser.testing import Browser
>>> browser = Browser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')


Checkout
========

Checkout is possible for Repository content. Let's open a dockument in the
repository and look at its `metadata_preview` page. We do have a checkout link
but no checkin link:

>>> browser.open('http://localhost/++skin++cms/repository/online/'
...     '2007/01/rauchen-verbessert-die-welt/metadata_preview')
>>> checkout = browser.getLink('Checkout')
>>> checkout
<Link text='actionmenuicon[IMG] Checkout' ...>
>>> browser.getLink('Checkin')
Traceback (most recent call last):
  ...
LinkNotFoundError


Check the document out by clicking on the link:

>>> checkout.click()
>>> print browser.contents
<?xml version...
<!DOCTYPE ...
  Unbekannte Resource...


Checkin
=======

After checking out we see the checked out document and can check it in again.
There is of course no checkout button any more:

>>> checkout = browser.getLink('Checkout')
Traceback (most recent call last):
  ...
LinkNotFoundError
>>> browser.getLink('Checkin').click()
>>> browser.url
'http://localhost/++skin++cms/repository/online/2007/01/rauchen-verbessert-die-welt/@@view.html'
