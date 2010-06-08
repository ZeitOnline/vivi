=======
Authors
=======

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()
>>> principal = zeit.cms.testing.create_interaction()

>>> import lxml.etree
>>> import zeit.content.author.author
>>> import zeit.cms.repository.interfaces
>>> import zope.component

>>> shakespeare = zeit.content.author.author.Author()
>>> shakespeare.title = 'Sir'
>>> shakespeare.firstname = 'William'
>>> shakespeare.lastname = 'Shakespeare'
>>> shakespeare.vgwortid = 12345
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> repository['shakespeare'] = shakespeare
>>> shakespeare = repository['shakespeare']
>>> print lxml.etree.tostring(shakespeare.xml, pretty_print=True)
<author xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <title py:pytype="str">Sir</title>
  <firstname py:pytype="str">William</firstname>
  <lastname py:pytype="str">Shakespeare</lastname>
  <vgwortid py:pytype="int">12345</vgwortid>
  <display_name py:pytype="str">William Shakespeare</display_name>
</author>

The default display name is 'Firstname Lastname', but any user-entered value
takes precedence:

>>> shakespeare.display_name = 'Flub'
>>> repository['shakespeare'] = shakespeare
>>> shakespeare = repository['shakespeare']
>>> print lxml.etree.tostring(shakespeare.xml, pretty_print=True)
<author xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <title py:pytype="str">Sir</title>
  <firstname py:pytype="str">William</firstname>
  <lastname py:pytype="str">Shakespeare</lastname>
  <vgwortid py:pytype="int">12345</vgwortid>
  <display_name py:pytype="str">Flub</display_name>
  <entered_display_name py:pytype="str">Flub</entered_display_name>
</author>

>>> shakespeare.display_name = None
>>> repository['shakespeare'] = shakespeare
>>> shakespeare = repository['shakespeare']
>>> print lxml.etree.tostring(shakespeare.xml, pretty_print=True)
<author xmlns:py="http://codespeak.net/lxml/objectify/pytype">
  <title py:pytype="str">Sir</title>
  <firstname py:pytype="str">William</firstname>
  <lastname py:pytype="str">Shakespeare</lastname>
  <vgwortid py:pytype="int">12345</vgwortid>
  <display_name py:pytype="str">William Shakespeare</display_name>
  <entered_display_name xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:nil="true"/>
</author>


Using authors
=============

The field author_references on ICommonMetadata is used to store authors:

>>> with zeit.cms.checkout.helper.checked_out(repository['testcontent']) as co:
...     co.author_references = [shakespeare]
>>> print lxml.etree.tostring(repository['testcontent'].xml, pretty_print=True)
<testtype>
  <head>
    <author ... href="http://xml.zeit.de/shakespeare">
      <firstname py:pytype="str">William</firstname>
      <lastname py:pytype="str">Shakespeare</lastname>
      <vgwortid py:pytype="int">12345</vgwortid>
      <display_name py:pytype="str">William Shakespeare</display_name>
    </author>
    ...
  </head>
  <body/>
</testtype>
