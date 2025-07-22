import zope.interface


class IMediaService(zope.interface.Interface):
    def get_audios(self):
        """Returns a list of audio files."""
