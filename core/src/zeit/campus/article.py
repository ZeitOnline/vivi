import zope.interface

import zeit.cms.content.reference

import zeit.campus.interfaces


class TopicpageLink(zeit.cms.related.related.RelatedBase):

    zope.interface.implements(zeit.campus.interfaces.ITopicpageLink)

    topicpage = zeit.cms.content.reference.SingleResource(
        '.head.topicpagelink', 'related')

    label = zeit.cms.content.property.ObjectPathProperty(
        '.head.topicpagelink.label',
        zeit.campus.interfaces.ITopicpageLink['label'])
