import zope.interface

import zeit.cms.content.reference

import zeit.campus.interfaces


class Topic(zeit.cms.related.related.RelatedBase):

    zope.interface.implements(zeit.campus.interfaces.ITopic)

    page = zeit.cms.content.reference.SingleResource(
        '.head.topic', 'related')

    label = zeit.cms.content.property.ObjectPathProperty(
        '.head.topic.label',
        zeit.campus.interfaces.ITopic['label'])
