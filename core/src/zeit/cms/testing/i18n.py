import zope.i18n.interfaces
import zope.interface


@zope.interface.implementer(zope.i18n.interfaces.IGlobalMessageCatalog)
class TestCatalog:
    language = 'tt'
    messages = {}

    def queryMessage(self, msgid, default=None):
        return self.messages.get(msgid, default)

    getMessage = queryMessage

    def getIdentifier(self):
        return 'test'

    def reload(self):
        pass
