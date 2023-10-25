import zope.interface


class ISimplecast(zope.interface.Interface):

    def synchronize_episode(self, episode_id: str):
        """Create, update, publish or retract episode with given id"""
