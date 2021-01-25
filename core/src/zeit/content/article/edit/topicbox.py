# -*- coding: utf-8 -*-
from six.moves import filter
from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import itertools
import zeit.cms.content.reference
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.image.interfaces
import zope.component


@grok.implementer(zeit.content.article.edit.interfaces.ITopicbox)
class Topicbox(zeit.content.article.edit.block.Block):

    type = 'topicbox'
    cssClass = 'topicbox'

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

    show_manuell = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'show_manuell',
        zeit.content.article.edit.interfaces.ITopicbox['show_manuell'],
        use_default=True)

    elasticsearch_raw_query = zeit.cms.content.property.ObjectPathProperty(
        '.elasticsearch_raw_query',
        zeit.content.article.edit.interfaces.ITopicbox[
            'elasticsearch_raw_query'])

    elasticsearch_raw_order = zeit.cms.content.property.ObjectPathProperty(
        '.elasticsearch_raw_order',
        zeit.content.article.edit.interfaces.ITopicbox[
            'elasticsearch_raw_order'], use_default=True)

    centerpage = zeit.cms.content.property.SingleResource('.centerpage')

    source_type = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'source_type',
        zeit.content.article.edit.interfaces.ITopicbox['source_type'])

    topicpage = zeit.cms.content.property.ObjectPathProperty(
        '.topicpage',
        zeit.content.article.edit.interfaces.ITopicbox['topicpage'])

    topicpage_filter = zeit.cms.content.property.ObjectPathProperty(
        '.topicpage_filter',
        zeit.content.article.edit.interfaces.ITopicbox['topicpage_filter'])

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
            parent_article = zeit.content.article.interfaces.IArticle(
                self, None)
            return itertools.islice(
                filter(
                    lambda x: x != parent_article,
                    zeit.edit.interfaces.IElementReferences(
                        self.referenced_cp)),
                len(self._reference_properties))
        return (content for content in self._reference_properties if content)


@zope.component.adapter(zeit.content.article.edit.interfaces.ITopicbox)
@zope.interface.implementer(zeit.content.image.interfaces.IImages)
class TopicboxImages(zeit.cms.related.related.RelatedBase):

    image = zeit.cms.content.reference.SingleResource('.image', 'image')

    fill_color = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.image', 'fill_color',
        zeit.content.image.interfaces.IImages['fill_color'])


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Topicbox
    title = _('Topicbox')
