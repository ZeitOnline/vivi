# -*- coding: utf-8 -*-
from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces


class Topicbox(zeit.content.article.edit.block.Block):

    grok.implements(zeit.content.article.edit.interfaces.ITopicbox)
    type = 'topicbox'

    supertitle = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'supertitle', zeit.content.article.edit.interfaces.ITopicbox['supertitle'])

    title = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'title', zeit.content.article.edit.interfaces.ITopicbox['title'])

    link = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'link', zeit.content.article.edit.interfaces.ITopicbox['link'])

    link_text = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'link_text',
        zeit.content.article.edit.interfaces.ITopicbox['link_text'])

    # first_reference = zeit.cms.content.reference.SingleResource(
    #     '.first_reference', 'first_reference')
    #
    # second_reference = zeit.cms.content.reference.SingleResource(
    #     '.second_reference', 'second_reference')
    #
    # third_reference = zeit.cms.content.reference.SingleResource(
    #     '.third_reference', 'third_reference')

    # related_content = zeit.cms.content.reference.MultiResource(
    #     '.related_content.reference', 'related')

    def values(self):
        return []


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Topicbox
    title = _('Topic Box')
