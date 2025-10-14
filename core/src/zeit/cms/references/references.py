import grokcore.component as grok
import zope.component

from zeit.cms.content.sources import FEATURE_TOGGLES
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.references.interfaces
import zeit.cms.repository.interfaces


@grok.subscribe(zeit.cms.interfaces.ICMSContent, zeit.cms.content.interfaces.IContentModifiedEvent)
def update_references(context, event):
    if not FEATURE_TOGGLES.find('store_references'):
        return

    repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
    references = extract(context)
    repository.update_references(context, references)


def extract(context):
    result = []
    for name, extract in sorted(
        zope.component.getAdapters((context,), zeit.cms.references.interfaces.IExtractReferences)
    ):
        result.extend(extract())
    return result


@grok.implementer(zeit.cms.references.interfaces.IExtractReferences)
class Extract(zeit.cms.grok.IndirectAdapter):
    grok.baseclass()

    def __call__(self):
        raise NotImplementedError()
