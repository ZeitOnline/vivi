# -*- coding: utf-8 -*-
from zeit.cms.i18n import MessageFactory as _
from zeit.content.article.edit.interfaces import TopicReferenceSource
from zeit.content.article.interfaces import IArticle
from zeit.cms.content.cache import cached_on_content
import grokcore.component as grok
import itertools
import logging
import lxml
import zeit.cms.content.reference
import zeit.contentquery.interfaces
import zeit.contentquery.helper
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.image.interfaces
import zope.component

log = logging.getLogger(__name__)


@grok.implementer(zeit.content.article.edit.interfaces.ITopicbox)
class Topicbox(zeit.content.article.edit.block.Block):

    start = 0
    type = 'topicbox'
    doc_iface = IArticle

    automatic_type = zeit.contentquery.helper.AutomaticTypeHelper()
    automatic_type.mapping = {None: 'manual'}

    count = zeit.contentquery.helper.CountHelper()
    query = zeit.contentquery.helper.QueryHelper()

    referenced_cp = zeit.contentquery.helper.ReferencedCenterpageHelper()

    is_complete_query = zeit.cms.content.property.ObjectPathProperty(
        '.elasticsearch_complete_query',
        zeit.content.article.edit.interfaces.ITopicbox['is_complete_query'],
        use_default=True)

    _count = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'count', zeit.content.article.edit.interfaces.ITopicbox['count'])

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

    hide_dupes = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'hide-dupes', zeit.content.article.edit.interfaces.ITopicbox[
            'hide_dupes'], use_default=True)

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
    def config_query(self):
        return self._config_query

    @config_query.setter
    def config_query(self, value):
        self._config_query = value

    def count_helper_tasks(self):
        pass

    @property
    def existing_teasers(self):
        return set()

    def _referenced_cp_get_helper_tasks(self):
        if self.automatic_type == 'manual':
            return self.get_centerpage_from_first_reference()

    @property
    def teaser_amount(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.article')
        return int(config['topicbox-teaser-amount'])

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

    @cached_on_content(IArticle, 'topicbox_values')
    def values(self):
        if self.referenced_cp:
            parent_article = zeit.content.article.interfaces.IArticle(self,
                                                                      None)
            return itertools.islice(
                filter(lambda x: x != parent_article,
                       zeit.edit.interfaces.IElementReferences(
                           self.referenced_cp)),
                len(self._reference_properties))

        if self.automatic_type == 'manual':
            return (
                content for content in self._reference_properties if content)

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
            return (
                content for content in self._reference_properties if content)

    @property
    def _content_query(self):
        content = zope.component.getAdapter(
            self, zeit.contentquery.interfaces.IContentQuery,
            name=self.automatic_type or '')
        return content

    def _serialize_query_item(self, item):
        typ = item[0]
        operator = item[1]
        field = zeit.content.cp.interfaces.IArea[
            'query'].value_type.type_interface[typ]

        if len(item) > self.teaser_amount:
            value = item[2:]
        else:
            value = item[2]
        if zope.schema.interfaces.ICollection.providedBy(field):
            value = field._type((value,))  # tuple(already_tuple) is a no-op
        value = self._converter(typ).toProperty(value)

        return typ, operator, value

    def _converter(self, selector):
        field = zeit.content.cp.interfaces.IArea[
            'query'].value_type.type_interface[selector]
        field = field.bind(zeit.content.article.interfaces.IArticle(self))
        props = zeit.cms.content.property.DAVConverterWrapper.DUMMY_PROPERTIES
        return zope.component.getMultiAdapter(
            (field, props),
            zeit.cms.content.interfaces.IDAVPropertyConverter)

    @property
    def existing_teasers(self):
        return set()

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
