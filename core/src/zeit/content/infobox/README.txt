=======
Infobox
=======

An infobox contains multiple blocks with additional information to an article.

Functional test setup:

>>> import zope.app.component.hooks
>>> old_site = zope.app.component.hooks.getSite()
>>> zope.app.component.hooks.setSite(getRootFolder())


The infobox has an attribute `contents` which contains the actuall data as a
tuple of tuples *yikes*.

>>> import zeit.content.infobox.infobox
>>> ib = zeit.content.infobox.infobox.Infobox()

Initially there are now entries:

>>> import lxml.etree
>>> print lxml.etree.tostring(ib.xml, pretty_print=True)
<container layout="artbox" label="info"/>

The title of an infobox is a supertitle:

>>> ib.supertitle = u'Altersvorsorge'
>>> print lxml.etree.tostring(ib.xml, pretty_print=True)
<container layout="artbox" label="info">
  <supertitle>Altersvorsorge</supertitle>
</container>

Add a contents element:

>>> ib.contents = (
...     ('Renteninformation', 'Nutzen Sie die Renteninformation, etc'),)
>>> ib.supertitle = u'Altersvorsorge'
>>> print lxml.etree.tostring(ib.xml, pretty_print=True)
<container layout="artbox" label="info">
  <supertitle>Altersvorsorge</supertitle>
  <block>
    <title>Renteninformation</title>
    <text>Nutzen Sie die Renteninformation, etc</text>
  </block>
</container>


>>> ib.contents = (
...     ('Informationen', 'Nutzen Sie die Renteninformation, etc'),
...     ('Fehlende Versicherungszeiten',
...      'Pruefen Sie, ob in Ihrer Renteninformation alle'))
>>> ib.supertitle = u'Altersvorsorge'
>>> print lxml.etree.tostring(ib.xml, pretty_print=True)
<container layout="artbox" label="info">
  <supertitle>Altersvorsorge</supertitle>
  <block>
    <title>Informationen</title>
    <text>Nutzen Sie die Renteninformation, etc</text>
  </block>
  <block>
    <title>Fehlende Versicherungszeiten</title>
    <text>Pruefen Sie, ob in Ihrer Renteninformation alle</text>
  </block>
</container>



Cleanup
=======

>>> zope.app.component.hooks.setSite(old_site)
