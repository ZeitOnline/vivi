import zope.interface
import zope.schema


class IAcceptedEntitlements(zope.interface.Interface):
    def __call__(self) -> set[str]:
        pass
