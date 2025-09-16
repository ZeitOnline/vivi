Portraitbox
===========

A portraitbox contains of title, text and an image.

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> principal = zeit.cms.testing.create_interaction()
>>> import zope.component
>>> import zeit.cms.repository.interfaces
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)


Let's instanciate a box and verify the xml:

>>> import zeit.content.portraitbox.portraitbox
>>> pb = zeit.content.portraitbox.portraitbox.Portraitbox()
>>> print(zeit.cms.testing.xmltotext(pb.xml))
<container layout="artbox" label="portrait"/>

Portraitbox is an asset:

>>> import zope.interface.verify
>>> import zeit.cms.interfaces
>>> import zeit.content.portraitbox.interfaces
>>> zope.interface.verify.verifyObject(
...     zeit.content.portraitbox.interfaces.IPortraitbox, pb)
True
>>> zope.interface.verify.verifyObject(
...     zeit.cms.interfaces.IAsset, pb)
True


Set data:

>>> import zeit.content.image.testing
>>> pb.name = 'Hans Wurst'
>>> pb.text = '<p><strong>Hans Wurst</strong> wursted hansig.</p>'
>>> repository['image'] = zeit.content.image.testing.create_image()
>>> pb.image = repository['image']
>>> print(zeit.cms.testing.xmltotext(pb.xml))
<container layout="artbox" label="portrait">
  <block>
    <title...>Hans Wurst</title>
    <text>
      <p>
      <strong>Hans Wurst</strong> wursted hansig.</p>
    </text>
    <image ...src="http://xml.zeit.de/image" type="jpeg"/>
  </block>
</container>

Verify the HTML support:

>>> import zeit.wysiwyg.interfaces
>>> html = zeit.wysiwyg.interfaces.IHTMLContent(pb)
>>> print(html.html)
<p><strong>Hans Wurst</strong> wursted hansig.</p>

When there is only text and no <p> node the contents is wrapped into a <p>
automatically:

>>> pb.text = 'ist <strong>ein Hans</strong> und wurstet.'
>>> print(html.html)
<p>ist <strong>ein Hans</strong> und wurstet.</p>


Verify the interface:

>>> import zope.interface.verify
>>> zope.interface.verify.verifyObject(
...     zeit.content.portraitbox.interfaces.IPortraitbox, pb)
True
