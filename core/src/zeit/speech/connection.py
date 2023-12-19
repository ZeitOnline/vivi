import zope.interface

import zeit.speech.interfaces


@zope.interface.implementer(zeit.speech.interfaces.ISpeech)
class Speech:
    def update(self, data: dict):
        pass
