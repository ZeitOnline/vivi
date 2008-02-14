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
<container xmlns:py="http://codespeak.net/lxml/objectify/pytype" layout="artbox" label="info"/>

The title of an infobox is a supertitle:

>>> ib.supertitle = u'Altersvorsorge'
>>> print lxml.etree.tostring(ib.xml, pretty_print=True)
<container xmlns:py="http://codespeak.net/lxml/objectify/pytype" layout="artbox" label="info">
  <supertitle py:pytype="str">Altersvorsorge</supertitle>
</container>

Add a contents element:

>>> ib.contents = (
...     ('Renteninformation', 'Nutzen Sie die Renteninformation, etc'),)
>>> ib.supertitle = u'Altersvorsorge'
>>> print lxml.etree.tostring(ib.xml, pretty_print=True)
<container xmlns:py="http://codespeak.net/lxml/objectify/pytype" layout="artbox" label="info">
  <supertitle py:pytype="str">Altersvorsorge</supertitle>
  <block>
    <title py:pytype="str">Renteninformation</title>
    <text py:pytype="str">Nutzen Sie die Renteninformation, etc</text>
  </block>
</container>


>>> ib.contents = (
...     ('Informationen', 'Nutzen Sie die Renteninformation, etc'),
...     ('Fehlende Versicherungszeiten',
...      'Pruefen Sie, ob in Ihrer Renteninformation alle'))
>>> ib.supertitle = u'Altersvorsorge'
>>> print lxml.etree.tostring(ib.xml, pretty_print=True)
<container xmlns:py="http://codespeak.net/lxml/objectify/pytype" layout="artbox" label="info">
  <supertitle py:pytype="str">Altersvorsorge</supertitle>
  <block>
    <title py:pytype="str">Informationen</title>
    <text py:pytype="str">Nutzen Sie die Renteninformation, etc</text>
  </block>
  <block>
    <title py:pytype="str">Fehlende Versicherungszeiten</title>
    <text py:pytype="str">Pruefen Sie, ob in Ihrer Renteninformation alle</text>
  </block>
</container>

Of course we'll get the data back, in unicode:

>>> import pprint
>>> pprint.pprint(ib.contents)
((u'Informationen', u'Nutzen Sie die Renteninformation, etc'),
 (u'Fehlende Versicherungszeiten',
  u'Pruefen Sie, ob in Ihrer Renteninformation alle'))


Cleanup
=======

>>> zope.app.component.hooks.setSite(old_site)
