import zope.interface


class IConnection(zope.interface.Interface):
    def get_audio_infos(self, year, volume):
        """Returns information about available premium audio MP3s for a given volume. The result
        is a dict with one entry per mediasync id. Each entry has `url` and `duration` fields."""


class IKeycloak(zope.interface.Interface):
    def authenticate(self):
        """Authenticates vivi. Returns a authentication header with token if successful."""
