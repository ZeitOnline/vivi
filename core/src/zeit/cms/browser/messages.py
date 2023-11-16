from zope.cachedescriptors.property import Lazy as cachedproperty
import z3c.flashmessage.interfaces
import zope.component


class MessageList:
    @property
    def css_class(self):
        result = ['staticErrorText']
        if self.messages:
            result.append('haveMessages')
        if [x for x in self.messages if x.type == 'error']:
            result.append('haveError')
        return ' '.join(result)

    @cachedproperty
    def messages(self):
        receiver = zope.component.getUtility(z3c.flashmessage.interfaces.IMessageReceiver)
        return list(receiver.receive())
