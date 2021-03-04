from zeit.content.cp.centerpage import writeabledict
from zeit.content.cp.interfaces import IAutomaticTeaserBlock, ICenterPage
from zope.cachedescriptors.property import Lazy as cachedproperty
import grokcore.component as grok
import logging
import zeit.cms.interfaces
import zeit.cms.content.interfaces
import zeit.content.cp.blocks.teaser
import zeit.content.cp.blocks.rss
import zeit.content.cp.interfaces
import zeit.contentquery.interfaces
import zeit.retresco.content
import zeit.retresco.interfaces
import zope.component


log = logging.getLogger(__name__)


def parent_cache(context, doc_iface, name, factory=writeabledict):
    parent = doc_iface(context)
    return parent.cache.setdefault(name, factory())


def cached_on_parent(
        doc_iface, attr=None, keyfunc=lambda x: x, factory=writeabledict):
    """ Decorator to cache the results of the function in a dictionary
        on the centerpage.  The dictionary keys are built using the optional
        `keyfunc`, which is called with `self` as a single argument. """
    def decorator(fn):
        def wrapper(self, *args, **kw):
            cache = parent_cache(self, doc_iface, attr or fn.__name__)
            key = keyfunc(self)
            if key not in cache:
                cache[key] = fn(self, *args, **kw)
            return cache[key]
        return wrapper
    return decorator


@zope.component.adapter(zeit.content.cp.interfaces.IArea)
@zope.interface.implementer(zeit.content.cp.interfaces.IRenderedArea)
class AutomaticArea(zeit.cms.content.xmlsupport.Persistent):

    start = 0  # Extension point for zeit.web to do pagination
    doc_iface = ICenterPage

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

    @cached_on_parent(ICenterPage, 'area_values', lambda x: x.context.__name__)
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

    @property
    @cached_on_parent(ICenterPage, keyfunc=lambda x: x.context.__name__)
    def existing_teasers(self):
        current_area = self.context
        cp = ICenterPage(self.context)
        area_teasered_content = parent_cache(
            cp, ICenterPage, 'area_teasered_content')
        area_manual_content = parent_cache(
            cp, ICenterPage, 'area_manual_content')

        seen = set()
        above = True
        for area in cp.cached_areas:
            if area == current_area:
                above = False
            if above:  # automatic teasers above current area
                if area not in area_teasered_content:
                    area_teasered_content[area] = set(
                        zeit.content.cp.interfaces.ITeaseredContent(area))
                seen.update(area_teasered_content[area])
            else:  # manual teasers below (or in) current area
                if area not in area_manual_content:
                    # Probably not worth a separate adapter (like
                    # ITeaseredContent), since the use case is pretty
                    # specialised.
                    area_manual_content[area] = set(
                        zeit.content.cp.blocks.teaser.extract_manual_teasers(
                            area))
                seen.update(area_manual_content[area])
        return seen

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
