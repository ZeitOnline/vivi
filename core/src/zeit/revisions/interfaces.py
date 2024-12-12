import zope.interface
import zope.schema


class IContentRevision(zope.interface.Interface):
    def __call__(self) -> set[str]:
        pass
