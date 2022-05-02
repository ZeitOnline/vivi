====================
Zeit CMS Syndication
====================

When the user publishes a document, he needs to choose where the document
should be published. He can choose one or more *syndication targets*.


Setup
-----

>>> import zeit.cms.testing
>>> zeit.cms.testing.set_site()

>>> def eventHandler(context, event):
...     print('Event: %s' % event)
...     for target in event.targets:
...         print('    Target: %s' % target.uniqueId)
...     print('    Content: %s' % context.uniqueId)
...
>>> import zope.component
>>> from zeit.cms.interfaces import ICMSContent
>>> from zeit.cms.syndication.interfaces import IContentSyndicatedEvent
>>> site_manager = zope.component.getGlobalSiteManager()
>>> site_manager.registerHandler(
...     eventHandler,
...     (ICMSContent, IContentSyndicatedEvent))
>>> import zeit.cms.testing
>>> principal = zeit.cms.testing.create_interaction()

>>> from zeit.cms.interfaces import ICMSContent
>>> from zeit.cms.repository.interfaces import IRepository
>>> repository = zope.component.getUtility(IRepository)
>>> content = repository['testcontent']
>>> ICMSContent.providedBy(content)
True


Syndication Targets
===================

A syndication target usually is a feed. Feeds are then integrated into
CenterPages to actually display the document.

The syndication target itself is an object in the backend of the CMS but unlike
real content it will not be checked out explicitly by the user. In fact it will
transparently be checked out by the CMS, modified and imediately checked back
in.

The user can choose which targets he is interested in. This is done via the
`IMySyndicationTargets` adapter.  After our test setup the user `bob` is
logged in.  We also get an object from he repository for later user. It
will be available as `content`.

To get his syndication targets we need his workingcopy:

>>> from zeit.cms.workingcopy.interfaces import IWorkingcopyLocation
>>> bobs_workingcopy = zope.component.getUtility(
...     IWorkingcopyLocation).getWorkingcopy()

Create some feeds we need for testing the defaults.

>>> import zeit.cms.repository.folder
>>> import zeit.cms.syndication.feed
>>> repository['hp_channels'] = zeit.cms.repository.folder.Folder()
>>> repository['hp_channels']['channel_news'] = (
...     zeit.cms.syndication.feed.Feed())
>>> repository['hp_channels']['channel_magazin'] = (
...     zeit.cms.syndication.feed.Feed())

The workingcopy can be adapted to `IMySyndicationTargets`:

>>> from zeit.cms.syndication.interfaces import IMySyndicationTargets
>>> bobs_syndication_targets = IMySyndicationTargets(bobs_workingcopy)
>>> bobs_syndication_targets
<zeit.cms.syndication.mytargets.MySyndicationTargets...>
>>> import zope.interface.verify
>>> zope.interface.verify.verifyObject(
...     IMySyndicationTargets, bobs_syndication_targets)
True

The syndication target object has an attribute `targets`, which initially is
filled with a default:

>>> bobs_syndication_targets.targets
<BTrees.OIBTree.OITreeSet...>
>>> len(bobs_syndication_targets.targets)
2
>>> list(bobs_syndication_targets.targets)
[<zeit.cms.content.keyreference.CMSContentKeyReference...>,
 <zeit.cms.content.keyreference.CMSContentKeyReference...>]
>>> default_targets = list(bobs_syndication_targets)
>>> default_targets
[<zeit.cms.syndication.feed.Feed...>,
 <zeit.cms.syndication.feed.Feed...>]

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
<zeit.cms.syndication.manager.SyndicationManager...>

Syndication of the object is possible:

>>> manager.canSyndicate
True

The available syndication targets are listed in the `targets` attribute. We
have added politk.feed to bob's targets above, so we have one target here:

>>> targets = manager.targets
>>> targets
[<zeit.cms.syndication.feed.Feed...>]
>>> len(targets)
1


Take the first target. It is empty so far:

>>> target = repository['politik.feed']
>>> list(target)
[]

When we syndicate to that target the `content` object is listed:

>>> manager.syndicate([target])
Event: <zeit.cms.syndication.interfaces.ContentSyndicatedEvent...>
     Target: http://xml.zeit.de/politik.feed
     Content: http://xml.zeit.de/testcontent
>>> target = repository['politik.feed']
>>> list(target)
[<zeit.cms.testcontenttype.testcontenttype.ExampleContentType...>]
>>> list(target)[0].uniqueId == content.uniqueId
True

>>> site_manager.unregisterHandler(
...     eventHandler,
...     (ICMSContent, IContentSyndicatedEvent))
True

Syndicating is not possible when the feed is locked by somebody else.

>>> import zeit.connector.interfaces
>>> connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
>>> connector.lock('http://xml.zeit.de/politik.feed', 'test.frodo', None)
>>> manager.syndicate([target])
Traceback (most recent call last):
    ...
SyndicationError: http://xml.zeit.de/politik.feed

Unlock again:

>>> connector.unlock('http://xml.zeit.de/politik.feed')


After syndication the relation utility knows where a content is syndicated in:

>>> import zeit.cms.relation.interfaces
>>> relations = zope.component.getUtility(
...     zeit.cms.relation.interfaces.IRelations)
>>> referenced_by = list(
...     relations.get_relations(content))
>>> len(referenced_by)
1


Setting feed metadata on syndication
====================================

It is possible to set the metadata from IEntry directly during syndication
using keyword arguments:

>>> repository['politik.feed'].getMetadata(content).hidden
False
>>> manager.syndicate([target], hidden=True)
>>> repository['politik.feed'].getMetadata(content).hidden
True
