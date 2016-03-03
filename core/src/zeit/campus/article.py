import zope.interface

import zeit.cms.content.reference

import zeit.campus.interfaces


class TopicpageLink(zeit.cms.related.related.RelatedBase):

    zope.interface.implements(zeit.campus.interfaces.ITopicpageLink)

    topicpagelink = zeit.cms.content.reference.MultiResource(
        '.head.topicpagelink.reference', 'related')
