import zope.interface

from zeit.cms.i18n import MessageFactory as _


class ISpeech(zope.interface.Interface):
    def update(self, data: dict):
        """Update audio object"""


class ISpeechbertChecksum(zope.interface.Interface):
    """Checksum of speechbert payload of article to validate consistency
    between audio and article body.
    """

    checksum = zope.schema.Text(title=_('Speechbert Checksum'), required=False)

    def validate(checksum: str) -> bool:
        """Valdiate context checksum against object checksum"""
