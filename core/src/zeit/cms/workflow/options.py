import grokcore.component as grok

from zeit.cms.workflow.interfaces import IManualPublicationOptions


@grok.implementer(IManualPublicationOptions)
class PublicationOptions:
    _unique_ids = ''

    @property
    def unique_ids(self):
        return self._unique_ids.split('\n')

    @unique_ids.setter
    def unique_ids(self, value):
        self._unique_ids = value

    @classmethod
    def from_dict(cls, options):
        obj = cls()
        for key, value in options.items():
            if key == 'unique_ids':
                obj.unique_ids = value
            else:
                setattr(obj, key, value)
        return obj


@grok.adapter(dict)
@grok.implementer(IManualPublicationOptions)
def options_factory(data):
    return PublicationOptions.from_dict(data)
