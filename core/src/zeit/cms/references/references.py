import grokcore.component as grok
import zope.component

import zeit.cms.checkout.interfaces
import zeit.cms.interfaces


@grok.subscribe(zeit.cms.interfaces.ICMSContent, zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def update_references(context, event):
    if not FEATURE_TOGGLES.find('store_references'):
        return

    if event.publishing:
        return

    references = extract(context)
    repository.update_references(context, references)


def extract(context):
    result = []
    for _, adapter in zope.component.getAdapters(context, zeit.cms.references.IReferenceExtract):
        result.extend(adapter)
    return result
