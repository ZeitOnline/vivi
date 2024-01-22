import zope.interface

from zeit.content.audio.interfaces import IAudio


class ISimplecast(zope.interface.Interface):
    def fetch_episode_audio(self, audio_id: str) -> dict:
        """Fetch audio data from simplecast given id"""

    def fetch_episode(self, episode_id: str) -> dict:
        """Fetch episode_data from simplecast given id"""

    def update(self, audio: IAudio, episode_data: dict):
        """Update audio object with episode_data from simplecast"""

    def synchronize_episode(self, episode_id: str):
        """Create, update, publish or retract episode with given id"""

    def publish(self, audio: IAudio):
        """Publish audio object"""


class TechnicalError(Exception):
    """Service had a technical error. The request can be retried."""

    def __init__(self, message, status):
        super().__init__(message)
        self.status = status
