import zope.interface

import zeit.mediaservice.interfaces


@zope.interface.implementer(zeit.mediaservice.interfaces.IConnection)
class MockConnection:
    def get_audio_infos(self, year, volume):
        return {
            1234: {
                'url': 'https://media-delivery.testing.de/d7f6ed45-18b8-45de-9e8f-1aef4e6a33a9.mp3',
                'duration': 'PT9M7S',
            },
            1235: {
                'url': 'https://media-delivery.testing.de/d7f6ed45-18b8-45de-9e8f-1aef4e6a33a9.mp3',
                'duration': 'PT12M',
            },
        }
