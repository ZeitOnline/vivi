Portraitbox
===========

A portraitbox contains of title, text and an image.

Let's instanciate a box and verify the xml[#functionaltest]_:

>>> import lxml.etree
>>> import zeit.content.portraitbox.portraitbox
>>> pb = zeit.content.portraitbox.portraitbox.Portraitbox()
>>> print lxml.etree.tostring(pb.xml, pretty_print=True)
<container xmlns:py="http://codespeak.net/lxml/objectify/pytype"
    layout="artbox" label="portrait"/>

Set data:

>>> pb.name = u'Hans Wurst'
>>> pb.text = u'<p><strong>Hans Wurst</strong> wursted hansig.</p>'
>>> pb.image = repository['2006']['DSC00109_2.JPG']
>>> print lxml.etree.tostring(pb.xml, pretty_print=True)
<container xmlns:py="http://codespeak.net/lxml/objectify/pytype" layout="artbox" label="portrait">
  <block>
    <title py:pytype="str">Hans Wurst</title>
    <text>
      <p><strong>Hans Wurst</strong> wursted hansig.</p>
    </text>
    <image xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" src="http://xml.zeit.de/2006/DSC00109_2.JPG" type="JPG">
      <bu xsi:nil="true"/>
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
<p xmlns...>ist <strong>ein Hans</strong> und wurstet.</p>


Verify the interface:

>>> import zope.interface.verify
>>> import zeit.content.portraitbox.interfaces
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




Clean up:

>>> zope.security.management.endInteraction()
>>> zope.app.component.hooks.setSite(old_site)


.. [#functionaltest] Functional test setup

    >>> import zope.app.component.hooks
    >>> old_site = zope.app.component.hooks.getSite()
    >>> zope.app.component.hooks.setSite(getRootFolder())

    >>> import zope.component
    >>> import zeit.cms.repository.interfaces
    >>> repository = zope.component.getUtility(
    ...     zeit.cms.repository.interfaces.IRepository)

    Also setup interaction

    >>> import zope.publisher.browser
    >>> request = zope.publisher.browser.TestRequest()
    >>> import zope.security.testing
    >>> principal = zope.security.testing.Principal(u'zope.user')
    >>> request.setPrincipal(principal)
    >>> import zope.security.management
    >>> zope.security.management.newInteraction(request)

