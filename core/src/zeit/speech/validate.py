import zope.interface

import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.speech.interfaces


@zope.interface.implementer(zeit.speech.interfaces.ISpeechbertChecksum)
class Speechbert(zeit.cms.content.dav.DAVPropertiesAdapter):
    checksum = zeit.cms.content.dav.DAVProperty(
        zeit.speech.interfaces.ISpeechbertChecksum['checksum'],
        zeit.cms.interfaces.SPEECHBERT_NAMESPACE,
        'checksum',
        writeable=zeit.cms.content.interfaces.WRITEABLE_LIVE,
    )

    def validate(self, checksum: str) -> bool:
        if not self.checksum or not checksum:
            return True
        return self.checksum == checksum
