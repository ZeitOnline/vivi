import zope.interface

import zeit.cms.content.reference

import zeit.campus.interfaces


class TopicpageLink(zeit.cms.related.related.RelatedBase):

    zope.interface.implements(zeit.campus.interfaces.ITopicpageLink)

    topicpagelink = zeit.cms.content.reference.SingleResource(
        '.head.topicpagelink', 'related')

    topicpagelink_label = zeit.cms.content.property.ObjectPathProperty(
        '.head.topicpagelink.label',
        zeit.campus.interfaces.ITopicpageLink['topicpagelink_label'])
