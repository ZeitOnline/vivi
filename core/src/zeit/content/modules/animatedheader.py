from urllib.parse import urlparse
from zope.cachedescriptors.property import Lazy as cachedproperty
import grokcore.component as grok
import zeit.cmp.interfaces
import zeit.cms.content.property
import zeit.content.modules.interfaces
import zeit.edit.block
import zope.interface


@zope.interface.implementer(zeit.content.modules.interfaces.IAnimatedHeader)
class AnimatedHeader(zeit.edit.block.Element):
    pass