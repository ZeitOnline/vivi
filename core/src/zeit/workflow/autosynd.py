# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import with_statement
import zeit.cms.checkout.helper
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.workflow.interfaces
import zope.component
import zope.interface


class AutoSynd(object):

    zope.component.adapts(zeit.cms.interfaces.IEditorialContent)
    zope.interface.implements(
        zeit.workflow.interfaces.IAutoSyndicationWorkflow)

    zeit.cms.content.dav.mapProperties(
        zeit.workflow.interfaces.IAutoSyndicationWorkflow,
        zeit.workflow.interfaces.WORKFLOW_NS,
        ('was_automatically_syndicated_into',), live=True)

    def __init__(self, context):
        self.context = context

    @property
    def automatically_syndicate_into(self):
        # Syndication rules -- those should be moved to a separate file like
        # the centerpage validation rules. But that's overkill for now.
        metadata = zeit.cms.content.interfaces.ICommonMetadata(
            self.context, None)
        if metadata is None or metadata.serie != u'News':
            return ()
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        channel = zeit.cms.interfaces.ICMSContent(
            config.get('news-channel'), None)
        if channel is None:
            return ()
        if channel in self.was_automatically_syndicated_into:
            return ()
        return (channel,)



@zope.component.adapter(AutoSynd)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def dav_properties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context, None)


@zope.component.adapter(
    zeit.cms.interfaces.IEditorialContent,
    zeit.cms.workflow.interfaces.IBeforePublishEvent)
def syndicate_before_publish(context, event):
    asw = zeit.workflow.interfaces.IAutoSyndicationWorkflow(context, None)
    if asw is None:
        return
    syndicated_to = []
    for channel in asw.automatically_syndicate_into:
        with zeit.cms.checkout.helper.checked_out(channel,
                                                  semantic_change=True) as co:
            if co is None:
                # Could not checkout
                continue
            co.insert(0, context)
            syndicated_to.append(channel)
    asw.was_automatically_syndicated_into += tuple(syndicated_to)


class Dependencies(object):

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(
        zeit.workflow.interfaces.IPublicationDependencies)

    def __init__(self, context):
        self.context = context

    def get_dependencies(self):
        asw = zeit.workflow.interfaces.IAutoSyndicationWorkflow(
            self.context, None)
        if asw is None:
            return []
        channels = []
        for channel in asw.was_automatically_syndicated_into:
            if channel.getPosition(self.context) == 1:
                channels.append(channel)
        return channels
