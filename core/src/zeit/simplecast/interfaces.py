import zope.interface


class ISimplecast(zope.interface.Interface):

    def get_episode(episode_id):
        """
        Request information about the episode from the simplecast API
        """
