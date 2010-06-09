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

>>> shakespeare.entered_display_name = 'Flub'
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

>>> shakespeare.entered_display_name = None
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

The field author_references on ICommonMetadata is used to store authors.
It takes precedence over the freetext authors:

>>> with zeit.cms.checkout.helper.checked_out(repository['testcontent']) as co:
...     co.author_references = [shakespeare]
...     co.authors = ['Charles Dickens']
>>> print lxml.etree.tostring(repository['testcontent'].xml, pretty_print=True)
<testtype>
  <head>
    <author ... href="http://xml.zeit.de/shakespeare" ...>
      <display_name py:pytype="str">William Shakespeare</display_name>
    </author>
    <attribute ... name="author">William Shakespeare</attribute>
    ...
  </head>
  <body/>
</testtype>

>>> with zeit.cms.checkout.helper.checked_out(repository['testcontent']) as co:
...     co.author_references = []
...     co.authors = ['Charles Dickens']
>>> print lxml.etree.tostring(repository['testcontent'].xml, pretty_print=True)
<testtype>
  <head>
    <attribute ... name="author">Charles Dickens</attribute>
    ...
  </head>
  <body/>
</testtype>


Publishing
==========

Authors are published along with the articles that reference them:

>>> with zeit.cms.checkout.helper.checked_out(repository['testcontent']) as co:
...     co.author_references = [repository['shakespeare']]

>>> zeit.cms.workflow.interfaces.IPublishInfo(
...     repository['testcontent']).urgent = True
>>> import transaction
>>> transaction.commit()
>>> job_id = zeit.cms.workflow.interfaces.IPublish(
...     repository['testcontent']).publish()
>>> import lovely.remotetask.interfaces
>>> tasks = zope.component.getUtility(
...     lovely.remotetask.interfaces.ITaskService, 'general')
>>> tasks.process()

>>> info = zeit.cms.workflow.interfaces.IPublishInfo(repository['shakespeare'])
>>> info.published
True


References
==========

We can track which articles an author is referenced by:

>>> import zeit.cms.relation.interfaces
>>> rel = zope.component.getUtility(
...     zeit.cms.relation.interfaces.IRelations)
>>> [x.uniqueId for x in rel.get_relations(repository['shakespeare'])]
[u'http://xml.zeit.de/testcontent']