import zope.interface


class ISimplecast(zope.interface.Interface):

    def publish_episode(self, episode_id: str):
        """Publish episode with given id"""

    def retract_episode(self, episode_id: str):
        """Retract episode with given id"""

    def create_episode(self, episode_id: str):
        """Create episode with given id"""

    def update_episode(self, episode_id: str):
        """Update episode data with given id"""

    def delete_episode(self, episode_id: str):
        """Delete episode with given id"""
