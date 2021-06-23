# -*- coding: utf-8 -*-
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.content.cache import cached_on_content
import grokcore.component as grok
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

    _preconfigured_query = zeit.cms.content.property.ObjectPathProperty(
        '.preconfigured_query',
        zeit.content.article.edit.interfaces.ITopicbox['preconfigured_query'])

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
    def preconfigured_query(self):
        return self._preconfigured_query

    @preconfigured_query.setter
    def preconfigured_query(self, value):
        self._preconfigured_query = value

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

    def get_centerpage_from_first_reference(self):
        import zeit.content.cp.interfaces
        if zeit.content.cp.interfaces.ICenterPage.providedBy(
                self.first_reference):
            return self.first_reference

    @cached_on_content('topicbox_values')
    def values(self):
        try:
            content = self._content_query()
        except LookupError:
            log.warning('%s found no IContentQuery type %s',
                        self, self.automatic_type)
            return ()

        parent_article = zeit.content.article.interfaces.IArticle(self)
        result = []
        while len(result) < 3:
            try:
                item = content.pop(0)
            except IndexError:
                break
            if item in result or item == parent_article:
                continue
            result.append(item)
        return result

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
