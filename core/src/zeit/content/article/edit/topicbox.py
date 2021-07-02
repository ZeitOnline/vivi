# -*- coding: utf-8 -*-
from zeit.cms.content.cache import cached_on_content
from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import logging
import zeit.cms.content.reference
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.content.image.interfaces
import zeit.contentquery.configuration
import zeit.contentquery.interfaces
import zope.app.appsetup.product
import zope.component

log = logging.getLogger(__name__)


@grok.implementer(zeit.content.article.edit.interfaces.ITopicbox)
class Topicbox(zeit.content.article.edit.block.Block,
               zeit.contentquery.configuration.Configuration):

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

    # zeit.contentquery.interfaces.IConfiguration

    _automatic_type = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'automatic_type',
        zeit.content.article.edit.interfaces.ITopicbox['automatic_type'])

    _automatic_type_bbb = {None: 'centerpage'}

    hide_dupes = False

    # BBB automatic_type=manual
    first_reference = zeit.cms.content.reference.SingleResource(
        '.first_reference', 'related')
    second_reference = zeit.cms.content.reference.SingleResource(
        '.second_reference', 'related')
    third_reference = zeit.cms.content.reference.SingleResource(
        '.third_reference', 'related')

    # automatic_type=preconfigured-query
    preconfigured_query = zeit.cms.content.property.ObjectPathProperty(
        '.preconfigured_query',
        zeit.content.article.edit.interfaces.ITopicbox['preconfigured_query'])

    @property
    def count(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.article')
        return int(config['topicbox-teaser-amount'])

    existing_teasers = frozenset()

    @property
    def automatic_type(self):
        # Backward compatibility for depreciated topicboxes
        # Set automatic_type on 'manual' only at the old topicboxes.
        if self._automatic_type is None:
            if (self.first_reference, self.second_reference,
                    self.third_reference) != (None, None, None):
                return 'manual'
        return super().automatic_type

    @automatic_type.setter
    def automatic_type(self, value):
        super(type(self), type(self)).automatic_type.__set__(self, value)

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
