import grokcore.component as grok
import zope.interface

import zeit.cms.content.interfaces
import zeit.entitlements.interfaces


@grok.implementer(zeit.entitlements.interfaces.IAcceptedEntitlements)
class AcceptedEntitlements(grok.Adapter):
    grok.context(zeit.cms.content.interfaces.ICommonMetadata)

    def __call__(self) -> set[str]:
        content = self.context
        match content.access:
            case None | 'free' | 'dynamic':
                return set()
            case 'registration':
                return {'registration'}
            case 'abo':
                return {'zplus'}
            case _:
                raise ValueError(f'{content} has invalid access value: {content.access}')


@grok.implementer(zeit.entitlements.interfaces.IAcceptedEntitlements)
class NoEntitlements(grok.Adapter):
    grok.context(zope.interface.Interface)

    def __call__(self) -> set[str]:
        return set()
