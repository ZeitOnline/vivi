import zope.interface


class ISimplecast(zope.interface.Interface):

    def fetch_episode(self, episode_id):
        """Request episode data from simplecast, return json body"""
