=======
Infobox
=======

An infobox contains multiple blocks with additional information to an article.

The infobox has an attribute `contents` which contains the actuall data as a
tuple of tuples *yikes* [#functional]_:

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
((u'Informationen', u'<p>Nutzen Sie die Renteninformation, etc</p>\n'),
 (u'Fehlende Versicherungszeiten',
  u'<p>Pruefen Sie, ob in <strong>Ihrer</strong> Renteninformation alle</p>\n\n<p>Fitze fitze fatze</p>\n'))

.. [#functional] Functional test setup:

    >>> import zeit.cms.testing
    >>> zeit.cms.testing.set_site(locals())

    >>> import zope.publisher.browser
    >>> import zope.security.testing
    >>> principal = zope.security.testing.Principal(u'zope.user')
    >>> request = zope.publisher.browser.TestRequest()
    >>> request.setPrincipal(principal)
    >>> import zope.security.management
    >>> zope.security.management.newInteraction(request)
    
