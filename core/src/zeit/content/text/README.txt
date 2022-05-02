Text
====

Text is used to add/edit HTML or plain text in the CMS.

Implementation
++++++++++++++

>>> import zeit.content.text.text
>>> text = zeit.content.text.text.Text()
>>> text
<zeit.content.text.text.Text...>
>>> text.text = 'Mary had a little lamb.'
>>> text.text
'Mary had a little lamb.'


The text type has an encoding which specifies the desired encoding for storage.
It defaults to 'UTF-8':

>>> text.encoding
'UTF-8'

Text instance provide the IText interface:

>>> import zope.interface.verify
>>> import zeit.content.text.interfaces
>>> zope.interface.verify.verifyObject(
...     zeit.content.text.interfaces.IText, text)
True

... and the IAsset interface:

>>> zope.interface.verify.verifyObject(
...     zeit.cms.interfaces.IAsset, text)
True

There is an invariant which makes sure the ``text`` can be representet in
``encoding``. Currently we have no umlauts and UTF-8 encoding so everything is
fine:

>>> import zope.schema
>>> zope.schema.getValidationErrors(
...     zeit.content.text.interfaces.IText, text)
[('__name__', RequiredMissing('__name__'))]

The __name__ failed, so set one:

>>> text.__name__ = 'mytext'
>>> zope.schema.getValidationErrors(
...     zeit.content.text.interfaces.IText, text)
[]

Set a unicode string with characters which are outside of ISO8859-15:

>>> text.text = 'Mary had a little lamb \u2014 and is happy.'

Since we have UTF-8 encoding the string can be encoded:

>>> zope.schema.getValidationErrors(
...     zeit.content.text.interfaces.IText, text)
[]

When we change the encoding to ISO8859-15 the validation is no longer passed:

>>> text.encoding = 'ISO8859-15'
>>> failed = zope.schema.getValidationErrors(
...     zeit.content.text.interfaces.IText, text)
>>> failed
[(None, <CannotEncode 'charmap' codec can't encode character '\u2014' in position 23: character maps to <undefined>>)]
>>> error = failed[0][1]
>>> import zope.i18n
>>> zope.i18n.translate(error.doc())
'Could not encode charachters 23-24 to ISO8859-15 (\u2014): character maps to <undefined>'


Switching back to UTF-8 solves the problem:

>>> text.encoding = 'UTF-8'
>>> zope.schema.getValidationErrors(
...     zeit.content.text.interfaces.IText, text)
[]

Integration
+++++++++++

Let's add the text created above to the repository:

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> import zope.component
>>> import zeit.cms.repository.interfaces
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)


>>> repository['atext'] = text

Let's get the text from the repository:

>>> text = repository['atext']
>>> text
<zeit.content.text.text.Text...>
>>> text.text
'Mary had a little lamb \u2014 and is happy.'
>>> text.encoding
'UTF-8'


When we remove the stored encoding a encoding is guessed:

>>> connector = zope.component.getUtility(
...     zeit.connector.interfaces.IConnector)
>>> connector.changeProperties('http://xml.zeit.de/atext',
...     {('encoding', zeit.content.text.interfaces.DAV_NAMESPACE):
...         zeit.connector.interfaces.DeleteProperty})
>>> text = repository['atext']
>>> text.text
'Mary had a little lamb \u2014 and is happy.'
>>> text.encoding
'UTF-8'
