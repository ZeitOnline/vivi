from zeit.content.cp.area import cached_on_content
from zeit.content.cp.interfaces import IAutomaticTeaserBlock
from zope.cachedescriptors.property import Lazy as cachedproperty
import grokcore.component as grok
import logging
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.cp.blocks.rss
import zeit.content.cp.blocks.teaser
import zeit.content.cp.interfaces
import zeit.contentquery.interfaces
import zeit.contentquery.query
import zeit.retresco.content
import zeit.retresco.interfaces
import zope.component


log = logging.getLogger(__name__)


@zope.component.adapter(zeit.content.cp.interfaces.IArea)
@zope.interface.implementer(zeit.content.cp.interfaces.IRenderedArea)
class AutomaticArea(zeit.cms.content.xmlsupport.Persistent):

    start = 0  # Extension point for zeit.web to do pagination

    def __init__(self, context):
        self.context = context
        self.xml = self.context.xml
        self.__parent__ = self.context

    # Convenience: Delegate IArea to our context, so we can be used like one.
    def __getattr__(self, name):
        # There's no interface for xmlsupport.Persistent which could tell us
        # that this attribute needs special treatment.
        if name == '__parent__':
            return super(AutomaticArea, self).__getattr__(name)
        if name in zeit.content.cp.interfaces.IArea:
            return getattr(self.context, name)
        raise AttributeError(name)

    @cached_on_content('area_values', lambda x: x.context.__name__)
    def values(self):
        if not self.automatic:
            return self.context.values()

        try:
            content = self._content_query()
        except LookupError:
            log.warning('%s found no IContentQuery type %s',
                        self.context, self.automatic_type)
            return self.context.values()

        result = []
        for block in self.context.values():
            if not IAutomaticTeaserBlock.providedBy(block):
                result.append(block)
                continue
            # This assumes that the *first* block always has a leader layout,
            # since otherwise the first result that may_be_leader might be
            # given to a non-leader block.
            if self.context.require_lead_candidates and block.layout.is_leader:
                teaser = pop_filter(content, is_lead_candidate)
                if teaser is None:
                    teaser = pop_filter(content)
                    block.change_layout(self.context.default_teaser_layout)
            else:
                teaser = pop_filter(content)
            if teaser is None:
                continue
            block.insert(0, teaser)
            result.append(block)

        return result

    @cachedproperty
    def _content_query(self):
        return zope.component.getAdapter(
            self, zeit.contentquery.interfaces.IContentQuery,
            name=self.automatic_type or '')

    def filter_values(self, *interfaces):
        # XXX copy&paste from zeit.edit.container.Base.filter_values
        for child in self.values():
            if any([x.providedBy(child) for x in interfaces]):
                yield child


def pop_filter(items, predicate=None):
    """Remove the first object from the list for which predicate returns True;
    no predicate means no filtering.
    """
    for i, item in enumerate(items):
        if predicate is None or predicate(item):
            items.pop(i)
            return item


def is_lead_candidate(content):
    metadata = zeit.cms.content.interfaces.ICommonMetadata(content, None)
    if metadata is None:
        return False
    return metadata.lead_candidate


@grok.adapter(zeit.contentquery.interfaces.IContentQuery)
@grok.implementer(zeit.content.cp.interfaces.ICenterPage)
def query_to_centerpage(context):
    return zeit.content.cp.interfaces.ICenterPage(context.context, None)
