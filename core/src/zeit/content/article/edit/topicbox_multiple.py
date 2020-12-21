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


@grok.implementer(zeit.content.article.edit.interfaces.ITopicboxMultiple)
class TopicboxMultiple(zeit.content.article.edit.block.Block):

    type = 'topicbox_multiple'

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

    query = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'query',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['query'])

    query_order = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'query_order',
        zeit.content.article.edit.interfaces.ITopicboxMultiple['query_order'])
    
    first_reference = zeit.cms.content.reference.SingleResource(
        '.first_reference', 'related')

    second_reference = zeit.cms.content.reference.SingleResource(
        '.second_reference', 'related')

    third_reference = zeit.cms.content.reference.SingleResource(
        '.third_reference', 'related')

    # @property
    # def query(self):
    #     if not hasattr(self.xml, 'query'):
    #         return ()

    #     result = []
    #     for condition in self.xml.query.getchildren():
    #         typ = condition.get('type')
    #         if typ == 'Channel':  # BBB
    #             typ = 'channels'
    #         operator = condition.get('operator')
    #         if not operator:  # BBB
    #             operator = 'eq'
    #         value = self._converter(typ).fromProperty(six.text_type(condition))
    #         field = zeit.content.cp.interfaces.IArea[
    #             'query'].value_type.type_interface[typ]
    #         if zope.schema.interfaces.ICollection.providedBy(field):
    #             value = value[0]
    #         # CombinationWidget needs items to be flattened
    #         if not isinstance(value, tuple):
    #             value = (value,)
    #         result.append((typ, operator) + value)
    #     return tuple(result)


#class Factory(zeit.content.article.edit.block.BlockFactory):

#    produces = TopicboxMultiple
#    title = _('Topicbox Multiple')