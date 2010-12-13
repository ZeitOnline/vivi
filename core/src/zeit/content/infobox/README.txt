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

Verify interfaces. The infobox is editorial content, even though it is used as
an asset:

>>> import zope.interface.verify
>>> import zeit.cms.interfaces
>>> import zeit.content.infobox.interfaces
>>> zope.interface.verify.verifyObject(
...     zeit.content.infobox.interfaces.IInfobox, ib)
True
>>> zope.interface.verify.verifyObject(
...     zeit.cms.interfaces.IEditorialContent, ib)
True

Initially there are no entries:

>>> import lxml.etree
>>> print lxml.etree.tostring(ib.xml, pretty_print=True)
<container
    xmlns:py="http://codespeak.net/lxml/objectify/pytype"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    layout="artbox" label="info"/>


The title of an infobox is a supertitle:

>>> ib.supertitle = u'Altersvorsorge'
>>> print lxml.etree.tostring(ib.xml, pretty_print=True)
<container xmlns:py="http://codespeak.net/lxml/objectify/pytype" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" layout="artbox" label="info">
  <supertitle py:pytype="str">Altersvorsorge</supertitle>
</container>

Add a contents element:

>>> ib.contents = (
...     ('Renteninformation', '<p>Nutzen Sie die Renteninformation, etc</p>'),)
>>> ib.supertitle = u'Altersvorsorge'
>>> print lxml.etree.tostring(ib.xml, pretty_print=True)
<container xmlns:py="http://codespeak.net/lxml/objectify/pytype" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" layout="artbox" label="info">
  <supertitle py:pytype="str">Altersvorsorge</supertitle>
  <block>
    <title py:pytype="str">Renteninformation</title>
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
>>> ib.supertitle = u'Altersvorsorge'
>>> print lxml.etree.tostring(ib.xml, pretty_print=True)
<container xmlns:py="http://codespeak.net/lxml/objectify/pytype" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" layout="artbox" label="info">
  <supertitle py:pytype="str">Altersvorsorge</supertitle>
  <block>
    <title py:pytype="str">Informationen</title>
    <text>
      <p>Nutzen Sie die Renteninformation, etc</p>
    </text>
  </block>
  <block>
    <title py:pytype="str">Fehlende Versicherungszeiten</title>
    <text>
      <p>Pruefen Sie, ob in <strong>Ihrer</strong> Renteninformation alle</p>
      <p>Fitze fitze fatze</p>
    </text>
  </block>
</container>

Of course we'll get the data back, in unicode:

>>> import pprint
>>> pprint.pprint(ib.contents)
((u'Infor...
 (u'Fehle...
  u'<p>Prue...
