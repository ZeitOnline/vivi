import logging

from zope.cachedescriptors.property import Lazy as cachedproperty
import zope.component

from zeit.content.cp.area import cached_on_content
from zeit.content.cp.interfaces import IAutomaticTeaserBlock
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.cp.blocks.rss
import zeit.content.cp.blocks.teaser
import zeit.content.cp.interfaces
import zeit.contentquery.interfaces
import zeit.contentquery.query
import zeit.retresco.content
import zeit.retresco.interfaces


log = logging.getLogger(__name__)


@zope.component.adapter(zeit.content.cp.interfaces.IArea)
@zope.interface.implementer(zeit.content.cp.interfaces.IRenderedArea)
class AutomaticArea(zeit.cms.content.xmlsupport.Persistent):
    def __init__(self, context):
        self.context = context
        self.xml = self.context.xml
        self.__parent__ = self.context

    # Convenience: Delegate IArea to our context, so we can be used like one.
    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            # There's no interface for xmlsupport.Persistent which could tell
            # us that this attribute needs special treatment.
            if name == '__parent__':
                return super().__parent__
            if name in zeit.content.cp.interfaces.IArea:
                return getattr(self.context, name)
            raise

    @cached_on_content('area_values', lambda x: x.context.__name__)
    def values(self):
        if not self.automatic:
            return self.context.values()

        try:
            content = self._content_query()
        except LookupError:
            log.warning('%s found no IContentQuery type %s', self.context, self.automatic_type)
            return self.context.values()

        result = []
        for block in self.context.values():
            if not IAutomaticTeaserBlock.providedBy(block):
                result.append(block)
                continue
            try:
                teaser = content.pop(0)
            except IndexError:
                continue
            block.insert(0, teaser)
            result.append(block)

        return result

    @cachedproperty
    def _content_query(self):
        return zope.component.getAdapter(
            self, zeit.contentquery.interfaces.IContentQuery, name=self.automatic_type or ''
        )

    def filter_values(self, *interfaces):
        # XXX copy&paste from zeit.edit.container.Base.filter_values
        for child in self.values():
            if any(x.providedBy(child) for x in interfaces):
                yield child
