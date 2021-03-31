# -*- coding: utf-8 -*-
from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.interfaces import TopicReferenceSource
from zeit.cms.content.cache import cached_on_content
import grokcore.component as grok
import itertools
import logging
import zeit.cms.content.reference
import zeit.contentquery.interfaces
import zeit.contentquery.helper
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.image.interfaces
import zope.app.appsetup.product
import zope.component

log = logging.getLogger(__name__)


@grok.implementer(zeit.content.article.edit.interfaces.ITopicbox)
class Topicbox(zeit.content.article.edit.block.Block):

    start = 0
    type = 'topicbox'

    query = zeit.contentquery.helper.QueryHelper()

    is_complete_query = zeit.cms.content.property.ObjectPathProperty(
        '.elasticsearch_complete_query',
        zeit.content.article.edit.interfaces.ITopicbox['is_complete_query'],
        use_default=True)

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

    hide_dupes = False

    _automatic_type = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'automatic_type',
        zeit.content.article.edit.interfaces.ITopicbox['automatic_type'])

    first_reference = zeit.cms.content.reference.SingleResource(
        '.first_reference', 'related')

    second_reference = zeit.cms.content.reference.SingleResource(
        '.second_reference', 'related')

    third_reference = zeit.cms.content.reference.SingleResource(
        '.third_reference', 'related')

    elasticsearch_raw_query = zeit.cms.content.property.ObjectPathProperty(
        '.elasticsearch_raw_query',
        zeit.content.article.edit.interfaces.ITopicbox[
            'elasticsearch_raw_query'])

    elasticsearch_raw_order = zeit.cms.content.property.ObjectPathProperty(
        '.elasticsearch_raw_order',
        zeit.content.article.edit.interfaces.ITopicbox[
            'elasticsearch_raw_order'], use_default=True)

    _referenced_cp = zeit.cms.content.property.SingleResource('.referenced_cp')

    referenced_topicpage = zeit.cms.content.property.ObjectPathProperty(
        '.referenced_topicpage',
        zeit.content.article.edit.interfaces.ITopicbox['referenced_topicpage'])

    topicpage_filter = zeit.cms.content.property.ObjectPathProperty(
        '.topicpage_filter',
        zeit.content.article.edit.interfaces.ITopicbox['topicpage_filter'])

    _config_query = zeit.cms.content.property.ObjectPathProperty(
        '.config_query',
        zeit.content.article.edit.interfaces.ITopicbox['config_query'])

    @property
    def automatic_type(self):
        mapping = {None: 'manual'}
        if self._automatic_type in mapping:
            return mapping[self._automatic_type]
        return self._automatic_type

    @automatic_type.setter
    def automatic_type(self, value):
        self._automatic_type = value

    @property
    def count(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.article')
        return int(config['topicbox-teaser-amount'])

    @property
    def config_query(self):
        return self._config_query

    @config_query.setter
    def config_query(self, value):
        self._config_query = value

    @property
    def _teaser_count(self):
        return 0

    existing_teasers = frozenset()

    @property
    def referenced_cp(self):
        if self.automatic_type == 'manual':
            return self.get_centerpage_from_first_reference()
        elif self.automatic_type == 'centerpage':
            return self._referenced_cp

    @referenced_cp.setter
    def referenced_cp(self, value):
        self._referenced_cp = value

    @property
    def _reference_properties(self):
        return (self.first_reference,
                self.second_reference,
                self.third_reference)

    def get_centerpage_from_first_reference(self):
        import zeit.content.cp.interfaces
        if zeit.content.cp.interfaces.ICenterPage.providedBy(
                self.first_reference):
            return self.first_reference

    @cached_on_content('topicbox_values')
    def values(self):
        """This case returns the old centerpage topicbox with first_reference
        sets the centerpage. In that case automatic_type is always manual
        (default)"""
        if self.referenced_cp and self.automatic_type == 'manual':
            parent_article = zeit.content.article.interfaces.IArticle(
                self, None)
            return itertools.islice(
                filter(lambda x: x != parent_article,
                       zeit.edit.interfaces.IElementReferences(
                           self.referenced_cp)),
                len(self._reference_properties))

        """Old style topicbox with 3 manual references"""
        if self.automatic_type == 'manual':
            return (
                content for content in self._reference_properties if content)

        """All content query driven topicboxes"""
        try:
            filtered_content = []
            content = iter(self._content_query())
            if content is None:
                return ()

            while(len(filtered_content)) < 3:
                try:
                    item = next(content)
                    if item in filtered_content:
                        continue
                    allow_cp = self.automatic_type == 'centerpage'
                    if TopicReferenceSource(
                            allow_cp).verify_interface(item):
                        filtered_content.append(item)
                except StopIteration:
                    break
            return iter(filtered_content)

        except (LookupError, ValueError):
            log.warning('found no IContentQuery type %s',
                        self.automatic_type)
            return ()

    @property
    def _content_query(self):
        content = zope.component.getAdapter(
            self, zeit.contentquery.interfaces.IContentQuery,
            name=self.automatic_type or '')
        return content


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


@grok.adapter(zeit.contentquery.interfaces.IContentQuery)
@grok.implementer(zeit.content.article.interfaces.IArticle)
def query_to_article(context):
    return zeit.content.article.interfaces.IArticle(context.context, None)
