import zope.interface


class ISimplecast(zope.interface.Interface):
    def fetch_episode(self, episode_id):
        """Fetch episode_data from simplecast given id"""

    def update(self, audio, episode_data):
        """Update audio object with episode_data from simplecast"""

    def synchronize_episode(self, episode_id: str):
        """Create, update, publish or retract episode with given id"""

    def publish(self, audio):
        """Publish audio object"""
