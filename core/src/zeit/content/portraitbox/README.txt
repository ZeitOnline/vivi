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

>>> import lxml.etree
>>> import zeit.content.portraitbox.portraitbox
>>> pb = zeit.content.portraitbox.portraitbox.Portraitbox()
>>> print lxml.etree.tostring(pb.xml, pretty_print=True)
<container xmlns:py="http://codespeak.net/lxml/objectify/pytype"
    layout="artbox" label="portrait"/>

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

>>> pb.name = u'Hans Wurst'
>>> pb.text = u'<p><strong>Hans Wurst</strong> wursted hansig.</p>'
>>> pb.image = repository['2006']['DSC00109_2.JPG']
>>> print lxml.etree.tostring(pb.xml, pretty_print=True)
<container xmlns:py="http://codespeak.net/lxml/objectify/pytype" layout="artbox" label="portrait">
  <block>
    <title...>Hans Wurst</title>
    <text>
      <p><strong>Hans Wurst</strong> wursted hansig.</p>
    </text>
    <image ...src="http://xml.zeit.de/2006/DSC00109_2.JPG" type="JPG"...>
      <bu xsi:nil="true"/>
      <copyright...
    </image>
  </block>
</container>

Verify the HTML support:

>>> import zeit.wysiwyg.interfaces
>>> html = zeit.wysiwyg.interfaces.IHTMLContent(pb)
>>> print html.html
<p><strong>Hans Wurst</strong> wursted hansig.</p>

When there is only text and no <p> node the contents is wrapped into a <p>
automatically:

>>> pb.text = u'ist <strong>ein Hans</strong> und wurstet.'
>>> print html.html
<p>ist <strong>ein Hans</strong> und wurstet.</p>


Verify the interface:

>>> import zope.interface.verify
>>> zope.interface.verify.verifyObject(
...     zeit.content.portraitbox.interfaces.IPortraitbox, pb)
True


Referencing using IPortraitboxReference
=======================================

The IPortraitboxReference adapter allows referencing of portrait boxes in XML
content:

>>> import zeit.cms.testcontenttype.testcontenttype
>>> content = zeit.cms.testcontenttype.testcontenttype.TestContentType()
>>> pb_ref = zeit.content.portraitbox.interfaces.IPortraitboxReference(
...     content)
>>> repository['pb'] = pb
>>> pb_ref.portraitbox = pb
>>> print lxml.etree.tostring(content.xml, pretty_print=True)
<testtype xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <head>
    <attribute py:pytype="str" ns="http://namespaces.zeit.de/CMS/document"
        name="artbox_portrait">http://xml.zeit.de/pb</attribute>
  </head>
  <body/>
</testtype>

>>> pb_ref.portraitbox == pb
True
