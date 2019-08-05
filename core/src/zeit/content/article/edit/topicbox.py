# -*- coding: utf-8 -*-
import itertools
from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.cms.content.reference
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.image.interfaces
import zope.component


@grok.implementer(zeit.content.article.edit.interfaces.ITopicbox)
class Topicbox(zeit.content.article.edit.block.Block):

    type = 'topicbox'

    supertitle = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'supertitle',
        zeit.content.article.edit.interfaces.ITopicbox['supertitle'])

    title = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'title', zeit.content.article.edit.interfaces.ITopicbox['title'])

    link = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'link', zeit.content.article.edit.interfaces.ITopicbox['link'])

    link_text = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'link_text',
        zeit.content.article.edit.interfaces.ITopicbox['link_text'])

    first_reference = zeit.cms.content.reference.SingleResource(
        '.first_reference', 'related')

    second_reference = zeit.cms.content.reference.SingleResource(
        '.second_reference', 'related')

    third_reference = zeit.cms.content.reference.SingleResource(
        '.third_reference', 'related')

    @property
    def _reference_properties(self):
        return (self.first_reference,
                self.second_reference,
                self.third_reference)

    @property
    def referenced_cp(self):
        import zeit.content.cp.interfaces
        if zeit.content.cp.interfaces.ICenterPage.providedBy(
                self.first_reference):
            return self.first_reference

    def values(self):
        if self.referenced_cp:
            parent_article = zeit.content.article.interfaces.IArticle(self,
                                                                      None)
            return itertools.islice(
                itertools.ifilter(lambda x: x != parent_article,
                                  zeit.edit.interfaces.IElementReferences(
                                      self.referenced_cp)),
                len(self._reference_properties))
        return (content for content in self._reference_properties if content)


class TopicboxImages(zeit.cms.related.related.RelatedBase):

    zope.component.adapts(zeit.content.article.edit.interfaces.ITopicbox)
    zope.interface.implements(zeit.content.image.interfaces.IImages)

    image = zeit.cms.content.reference.SingleResource('.image', 'image')

    fill_color = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.image', 'fill_color',
        zeit.content.image.interfaces.IImages['fill_color'])


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Topicbox
    title = _('Topicbox')
