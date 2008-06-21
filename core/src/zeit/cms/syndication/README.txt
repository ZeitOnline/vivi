====================
Zeit CMS Syndication
====================

When the user publishes a document, he needs to choose where the document
should be published. He can choose one or more *syndication targets*. 


Syndication Targets
===================

A syndication target usually is a feed. Feeds are then integrated into
CenterPages to actually display the document.

The syndication target itself is an object in the backend of the CMS but unlike
real content it will not be checked out explicitly by the user. In fact it will
transparently be checked out by the CMS, modified and imediately checked back
in.

The user can choose which targets he is interested in. This is done via the
`IMySyndicationTargets` adapter.  After initialization[1]_ the user `bob` is
logged in.  We also get an object from he repository[2]_ for later user. It
will be available as `content`.

To get his syndication targets we need his workingcopy:

>>> from zeit.cms.workingcopy.interfaces import IWorkingcopyLocation
>>> bobs_workingcopy = zope.component.getUtility(
...     IWorkingcopyLocation).getWorkingcopy()

The workingcopy can be adapted to `IMySyndicationTargets` [#create-feeds]_:

>>> from zeit.cms.syndication.interfaces import IMySyndicationTargets
>>> bobs_syndication_targets = IMySyndicationTargets(bobs_workingcopy)
>>> bobs_syndication_targets
<zeit.cms.syndication.mytargets.MySyndicationTargets object at 0x...>
>>> import zope.interface.verify
>>> zope.interface.verify.verifyObject(
...     IMySyndicationTargets, bobs_syndication_targets)
True    

The syndication target object has an attribute `targets`, which initially is
filled with a default:

>>> bobs_syndication_targets.targets
<BTrees.OIBTree.OITreeSet object at 0x...>
>>> len(bobs_syndication_targets.targets)
2
>>> list(bobs_syndication_targets.targets)
[<zeit.cms.content.keyreference.CMSContentKeyReference object at 0x...>,
 <zeit.cms.content.keyreference.CMSContentKeyReference object at 0x...>]
>>> default_targets = list(bobs_syndication_targets)
>>> default_targets
[<zeit.cms.syndication.feed.Feed object at 0x...>,
 <zeit.cms.syndication.feed.Feed object at 0x...>]

We have two feeds in the demo system, get them:

>>> politik = repository['politik.feed']
>>> wirtschaft = repository['wirtschaft.feed']

Add the politik feed to the targets:

>>> politik in bobs_syndication_targets
False
>>> bobs_syndication_targets.add(politik)
>>> politik in bobs_syndication_targets
True

Remove the default targets:

>>> bobs_syndication_targets.remove(default_targets[0])
>>> bobs_syndication_targets.remove(default_targets[1])


Syndication Manager
===================

A syndication manager is an adapter to a content object.  Now get the
syndication manager:

>>> from zeit.cms.syndication.interfaces import ISyndicationManager
>>> manager = ISyndicationManager(content)
>>> manager
<zeit.cms.syndication.manager.SyndicationManager object at 0x...>

Syndication of the object is possible:

>>> manager.canSyndicate
True

The available syndication targets are listed in the `targets` attribute. We
have added politk.feed to bob's targets above, so we have one target here:

>>> targets = manager.targets
>>> targets
[<zeit.cms.syndication.feed.Feed object at 0x...>]
>>> len(targets)
1


Take the first target. It is empty so far:

>>> target = repository['politik.feed']
>>> list(target)
[]

When we syndicate to that target the `content` object is listed:

>>> manager.syndicate([target])
Event: <zeit.cms.syndication.interfaces.ContentSyndicatedEvent object at 0x...>
     Target: http://xml.zeit.de/politik.feed
     Content: http://xml.zeit.de/testcontent
>>> target = repository['politik.feed']
>>> list(target)
[<zeit.cms.testcontenttype.testcontenttype.TestContentType object at 0x...>]
>>> list(target)[0].uniqueId == content.uniqueId
True

Syndicating is not possible when the feed is locked by somebody else.

>>> import zeit.connector.interfaces
>>> connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
>>> connector.lock(u'http://xml.zeit.de/politik.feed', 'test.frodo', None)
>>> manager.syndicate([target])
Traceback (most recent call last):
    ...
SyndicationError: http://xml.zeit.de/politik.feed

Unlock again:

>>> connector.unlock(u'http://xml.zeit.de/politik.feed')


After syndication the relation utility knows where a content is syndicated in:

>>> import zeit.cms.relation.interfaces
>>> relations = zope.component.getUtility(
...     zeit.cms.relation.interfaces.IRelations)
>>> syndicated_in = list(
...     relations.get_relations(content, 'syndicated_in'))
>>> len(syndicated_in)
1

Automatic update of metadata
============================

When an object is checked in its metadata is copied to the feeds it is
syndicated in automatically.

Check the source of the feed first:

>>> import lxml.etree
>>> print lxml.etree.tostring(repository['politik.feed'].xml,
...     pretty_print=True)
<channel>
  <title>Politik</title>
  <container>
    <block xmlns:py="http://codespeak.net/lxml/objectify/pytype" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" href="http://xml.zeit.de/testcontent">
      <supertitle xsi:nil="true"/>
      <title xsi:nil="true"/>
      <text xsi:nil="true"/>
      <byline xsi:nil="true"/>
      <short>
        <title xsi:nil="true"/>
        <text xsi:nil="true"/>
      </short>
      <homepage>
        <title xsi:nil="true"/>
        <text xsi:nil="true"/>
      </homepage>
      <references/>
    </block>
  </container>
  <object_limit xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="int">50</object_limit>
</channel>


Checkout content, change a teaser and check back in:

>>> import zeit.cms.checkout.interfaces
>>> checked_out = zeit.cms.checkout.interfaces.ICheckoutManager(
...     content).checkout()
>>> checked_out.teaserTitle = u'nice Teaser Title'
>>> zeit.cms.checkout.interfaces.ICheckinManager(checked_out).checkin()
<zeit.cms.testcontenttype.testcontenttype.TestContentType object at 0x...>

Verify the channel source again:

>>> print lxml.etree.tostring(repository['politik.feed'].xml,
...     pretty_print=True)
<channel>
  <title>Politik</title>
  <container>
    <block xmlns:py="http://codespeak.net/lxml/objectify/pytype" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" href="http://xml.zeit.de/testcontent">
      <supertitle xsi:nil="true"/>
      <title py:pytype="str">nice Teaser Title</title>
      <text xsi:nil="true"/>
      <byline xsi:nil="true"/>
      <short>
        <title xsi:nil="true"/>
        <text xsi:nil="true"/>
      </short>
      <homepage>
        <title xsi:nil="true"/>
        <text xsi:nil="true"/>
      </homepage>
      <references/>
    </block>
  </container>
  <object_limit xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="int">50</object_limit>
</channel>


Forbid the automatic update:

>>> checked_out = zeit.cms.checkout.interfaces.ICheckoutManager(
...     content).checkout()
>>> checked_out.teaserTitle = u'Bite my shiny metal ass.'
>>> checked_out.automaticMetadataUpdateDisabled = frozenset([
...     repository['politik.feed']])
>>> zeit.cms.checkout.interfaces.ICheckinManager(checked_out).checkin()
<zeit.cms.testcontenttype.testcontenttype.TestContentType object at 0x...>

The feed has not changed this time:

>>> print lxml.etree.tostring(repository['politik.feed'].xml,
...     pretty_print=True)
<channel>
  <title>Politik</title>
  <container>
    <block xmlns:py="http://codespeak.net/lxml/objectify/pytype" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" href="http://xml.zeit.de/testcontent">
      <supertitle xsi:nil="true"/>
      <title py:pytype="str">nice Teaser Title</title>
      <text xsi:nil="true"/>
      <byline xsi:nil="true"/>
      <short>
        <title xsi:nil="true"/>
        <text xsi:nil="true"/>
      </short>
      <homepage>
        <title xsi:nil="true"/>
        <text xsi:nil="true"/>
      </homepage>
      <references/>
    </block>
  </container>
  <object_limit xmlns:py="http://codespeak.net/lxml/objectify/pytype" py:pytype="int">50</object_limit>
</channel>


The metadata update doesn't fail when the content is removed from the feed
under the hood.

>>> politik = repository['politik.feed']
>>> politik.remove(repository['testcontent'])
>>> repository.addContent(politik)
>>> len(repository['politik.feed'])
0

We need to re-enable the automatic update during checkout:

>>> checked_out = zeit.cms.checkout.interfaces.ICheckoutManager(
...     content).checkout()
>>> checked_out.automaticMetadataUpdateDisabled = frozenset([])
>>> zeit.cms.checkout.interfaces.ICheckinManager(checked_out).checkin()
<zeit.cms.testcontenttype.testcontenttype.TestContentType object at 0x...>

Even after checkout there is nothing in the feed:

>>> len(repository['politik.feed'])
0


Ordering of Content in a Feed
=============================

When new content is published into a feed it is inserted on the top making the
new document the first.

It is sometimes, if not often, necessary to apply a manual order to a feed's
content. For instance if an article is very important it should be kept on the
top until furhter notice. This mechanism we call pinnig.


Questions Regarding Implementation 
==================================

* The syndication targets reside in the backend, but we need to generate a
  list of them. This basically means we need a query like
  `backend.search(type='feed')`.

* At which point is the feed published to the production server? Is this a
  separate workflow step? Will feeds be published like any other content? Or
  will we publish documents together with the feed?


Cleanup
=======

After the test we restore the old site:

>>> zope.security.management.endInteraction()
>>> site_manager.unregisterHandler(
...     eventHandler,
...     (ICMSContent, IContentSyndicatedEvent))
True
>>> zope.app.component.hooks.setSite(old_site)


Footnotes
=========

.. [1] Initialization:

    >>> import zope.app.component.hooks
    >>> old_site = zope.app.component.hooks.getSite()
    >>> zope.app.component.hooks.setSite(getRootFolder())

    >>> def eventHandler(context, event):
    ...     print 'Event:', event
    ...     for target in event.targets:
    ...         print '    Target:', target.uniqueId
    ...     print '    Content:', context.uniqueId
    ...
    >>> import zope.component
    >>> from zeit.cms.interfaces import ICMSContent
    >>> from zeit.cms.syndication.interfaces import IContentSyndicatedEvent
    >>> site_manager = zope.component.getSiteManager()
    >>> site_manager.registerHandler(
    ...     eventHandler,
    ...     (ICMSContent, IContentSyndicatedEvent))

    Log in bob:

    >>> import zope.security.testing
    >>> principal = zope.security.testing.Principal(u'bob')
    >>> participation = zope.security.testing.Participation(principal)
    >>> import zope.security.management
    >>> zope.security.management.newInteraction(participation)


.. [2] Get content from the repository:

    >>> from zeit.cms.interfaces import ICMSContent
    >>> from zeit.cms.repository.interfaces import IRepository
    >>> repository = zope.component.getUtility(IRepository)
    >>> content = repository['testcontent']
    >>> ICMSContent.providedBy(content)
    True


.. [#create-feeds] Create some feeds we need for testing the defaults.

    >>> import zeit.cms.repository.folder
    >>> import zeit.cms.syndication.feed
    >>> repository['hp_channels'] = zeit.cms.repository.folder.Folder()
    >>> repository['hp_channels']['channel_news'] = (
    ...     zeit.cms.syndication.feed.Feed())
    >>> repository['hp_channels']['channel_magazin'] = (
    ...     zeit.cms.syndication.feed.Feed())
    

    
