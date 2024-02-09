=======
Infobox
=======

An infobox contains multiple blocks with additional information to an article.

The infobox has an attribute `contents` which contains the actuall data as a
tuple of tuples *yikes*:

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> principal = zeit.cms.testing.create_interaction()
>>> import zeit.content.infobox.infobox
>>> ib = zeit.content.infobox.infobox.Infobox()

Verify interfaces. The infobox is used as an asset:

>>> import zope.interface.verify
>>> import zeit.cms.interfaces
>>> import zeit.content.infobox.interfaces
>>> zope.interface.verify.verifyObject(
...     zeit.content.infobox.interfaces.IInfobox, ib)
True
>>> zope.interface.verify.verifyObject(
...     zeit.cms.interfaces.IAsset, ib)
True

Initially there are no entries:

>>> print(zeit.cms.testing.xmltotext(ib.xml))
<container layout="artbox" label="info"/>


The title of an infobox is a supertitle:

>>> ib.supertitle = 'Altersvorsorge'
>>> print(zeit.cms.testing.xmltotext(ib.xml))
<container layout="artbox" label="info">
  <supertitle...>Altersvorsorge</supertitle>
</container>

Add a contents element:

>>> ib.contents = (
...     ('Renteninformation', '<p>Nutzen Sie die Renteninformation, etc</p>'),)
>>> ib.supertitle = 'Altersvorsorge'
>>> print(zeit.cms.testing.xmltotext(ib.xml))
<container layout="artbox" label="info">
  <supertitle...>Altersvorsorge</supertitle>
  <block>
    <title>Renteninformation</title>
    <text>
      <p>Nutzen Sie die Renteninformation, etc</p>
    </text>
  </block>
</container>


>>> ib.contents = (
...     ('Informationen', '<p>Nutzen Sie die Renteninformation, etc</p>'),
...     ('Fehlende Versicherungszeiten',
...      '<p>Pruefen Sie, ob in <strong>Ihrer</strong> Renteninformation '
...      'alle</p><p>Fitze fitze fatze</p>'))
>>> ib.supertitle = 'Altersvorsorge'
>>> print(zeit.cms.testing.xmltotext(ib.xml))
<container layout="artbox" label="info">
  <supertitle...>Altersvorsorge</supertitle>
  <block>
    <title>Informationen</title>
    <text>
      <p>Nutzen Sie die Renteninformation, etc</p>
    </text>
  </block>
  <block>
    <title>Fehlende Versicherungszeiten</title>
    <text>
      <p>Pruefen Sie, ob in <strong>Ihrer</strong> Renteninformation alle</p>
      <p>Fitze fitze fatze</p>
    </text>
  </block>
</container>

Of course we'll get the data back, in unicode:

>>> import pprint
>>> pprint.pprint(ib.contents)
(('Infor...
 ('Fehle...
  '<p>Prue...
