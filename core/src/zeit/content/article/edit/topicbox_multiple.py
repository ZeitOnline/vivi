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
import gocept.form.grouped
import logging

log = logging.getLogger(__name__)


class ReferencedCpFallbackProperty(
        zeit.cms.content.property.ObjectPathProperty):
    """
    Special ObjectPathProperty which looks up an attribute
    from the referenced cp as a fallback.
    """

    def __get__(self, instance, class_):
        value = super(ReferencedCpFallbackProperty, self).__get__(
            instance, class_)
        if value == self.field.missing_value and instance.referenced_cp:
            value = getattr(instance.referenced_cp,
                            self.field.__name__,
                            self.field.default)
        return value


@grok.implementer(zeit.content.article.edit.interfaces.ITopicboxMultiple)
class TopicboxMultiple(zeit.content.article.edit.block.Block):

    type = 'topicbox_multiple'

    _source = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'source',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['source'])

    _source_type = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'source_type',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['source_type'])

    _centerpage = zeit.cms.content.property.SingleResource('.centerpage')

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        if self.source and not value:
            self._materialize_auto_blocks()
        self._source = value
        if value:
            self._create_auto_blocks()

    @property
    def source_type(self):
        result = self._source_type
        if result == 'channel':  # BBB
            result = 'custom'
        return result

    @source_type.setter
    def source_type(self, value):
        self._source_type = value

    _count = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'count', zeit.content.article.edit.interfaces.ITopicboxMultiple['count'])

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        if not value:
            self._count = 3
        else:
            self._count = value

    @property
    def centerpage(self):
        return self._centerpage

    @centerpage.setter
    def centerpage(self, value):
        # It is still possible to build larger circles (e.g A->C->A)
        # but a sane user should not ignore the errormessage shown in the
        # cp-editor and preview.
        # Checking for larger circles is not reasonable here.
        if value.uniqueId == \
                zeit.content.cp.interfaces.ICenterPage(self).uniqueId:
            raise ValueError("A centerpage can't reference itself!")
        self._centerpage = value

    supertitle = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'supertitle',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['supertitle'])
    
    title = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'title', zeit.content.article.edit.interfaces.ITopicboxMultiple['title'])

    link = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'link', zeit.content.article.edit.interfaces.ITopicboxMultiple['link'])

    link_text = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'link_text',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['link_text'])

    first_reference = zeit.cms.content.reference.SingleResource(
        '.first_reference', 'related')

    second_reference = zeit.cms.content.reference.SingleResource(
        '.second_reference', 'related')

    third_reference = zeit.cms.content.reference.SingleResource(
        '.third_reference', 'related')

    query = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'query',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['query'])

    query_order = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'query_order',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['query_order'])

    hide_dupes = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'hide-dupes', zeit.content.article.edit.interfaces.ITopicboxMultiple['hide_dupes'],
        use_default=True)

    elasticsearch_raw_query = zeit.cms.content.property.ObjectPathProperty(
        '.elasticsearch_raw_query',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['elasticsearch_raw_query'])
    elasticsearch_raw_order = zeit.cms.content.property.ObjectPathProperty(
        '.elasticsearch_raw_order',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['elasticsearch_raw_order'],
        use_default=True)
    is_complete_query = zeit.cms.content.property.ObjectPathProperty(
        '.elasticsearch_complete_query',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['is_complete_query'],
        use_default=True)

    topicpage = zeit.cms.content.property.ObjectPathProperty(
        '.topicpage',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['topicpage'])
    topicpage_filter = zeit.cms.content.property.ObjectPathProperty(
        '.topicpage_filter',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['topicpage_filter'])
    is_complete_query = zeit.cms.content.property.ObjectPathProperty(
        '.elasticsearch_complete_query',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['is_complete_query'],
        use_default=True)

    rss_feed = zeit.cms.content.property.DAVConverterWrapper(
        zeit.cms.content.property.ObjectPathAttributeProperty('.', 'rss_feed'),
        zeit.content.article.edit.interfaces.ITopicboxMultiple['rss_feed'])

    topiclink_label_1 = ReferencedCpFallbackProperty(
        '.topiclink_label_1',
        zeit.content.cp.interfaces.IArea['topiclink_label_1'])

    topiclink_url_1 = ReferencedCpFallbackProperty(
        '.topiclink_url_1',
        zeit.content.cp.interfaces.IArea['topiclink_url_1'])

    topiclink_label_2 = ReferencedCpFallbackProperty(
        '.topiclink_label_2',
        zeit.content.cp.interfaces.IArea['topiclink_label_2'])

    topiclink_url_2 = ReferencedCpFallbackProperty(
        '.topiclink_url_2',
        zeit.content.cp.interfaces.IArea['topiclink_url_2'])

    topiclink_label_3 = ReferencedCpFallbackProperty(
        '.topiclink_label_3',
        zeit.content.cp.interfaces.IArea['topiclink_label_3'])

    topiclink_url_3 = ReferencedCpFallbackProperty(
        '.topiclink_url_3',
        zeit.content.cp.interfaces.IArea['topiclink_url_3'])

    def _create_auto_blocks(self):
        """Add automatic teaser blocks so we have #count of them.
        We _replace_ previously materialized ones, preserving their #layout
        (copying it to the auto block at the same position).

        """
        self.adjust_auto_blocks_to_count()

        order = self.keys()
        for block in self.values():
            if not block.volatile:
                continue

            auto_block = self.create_item('auto-teaser')
            auto_block.__name__ = block.__name__  # required to updateOrder

            if ITeaserBlock.providedBy(block):
                auto_block.layout = block.layout

            # Only deletes first occurrence of __name__, i.e. `block`
            del self[block.__name__]

        # Preserve order of blocks that are kept when turning AutoPilot on.
        self.updateOrder(order)

    def _materialize_auto_blocks(self):
        """Replace automatic teaser blocks by teaser blocks with same content
        and same attributes (e.g. `layout`).

        (Make sure this method only runs when #automatic is enabled, otherwise
        IRenderedArea will not retrieve results from the content query source.)

        """
        order = self.keys()
        for old in zeit.content.cp.interfaces.IRenderedArea(self).values():
            if not IAutomaticTeaserBlock.providedBy(old):
                continue

            # Delete automatic teaser first, since adding normal teaser will
            # delete the last automatic teaser via the
            # `adjust_auto_blocks_to_count` event handler.
            # (Deleting doesn't remove __name__ or __parent__, so we can still
            # copy those afterwards)
            del self[old.__name__]

            new = self.create_item('teaser')
            new.update(old)

        # Preserve order of non-auto blocks.
        self.updateOrder(order)

        # Remove unfilled auto blocks.
        for block in list(self.values()):
            if IAutomaticTeaserBlock.providedBy(block):
                del self[block.__name__]

class Factory(zeit.content.article.edit.block.BlockFactory):

   produces = TopicboxMultiple
   title = _('Topicbox Multiple')