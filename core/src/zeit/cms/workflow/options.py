import grokcore.component as grok

from zeit.cms.workflow.interfaces import IManualPublicationOptions


@grok.implementer(IManualPublicationOptions)
class PublicationOptions:
    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
