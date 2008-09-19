Centerpage
==========

The centerpage is an editorial content:

>>> import zope.interface.verify
>>> import zeit.cms.interfaces
>>> import zeit.content.centerpage.centerpage
>>> cp = zeit.content.centerpage.centerpage.CenterPage()
>>> zope.interface.verify.verifyObject(
...     zeit.cms.interfaces.IEditorialContent, cp)
True
