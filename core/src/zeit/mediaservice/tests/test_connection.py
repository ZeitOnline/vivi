import requests_mock

import zeit.mediaservice.testing


DATA = {
    '@context': 'https://schema.org',
    '@type': 'DataFeed',
    'dataFeedElement': [
        {
            '@type': 'DataFeedItem',
            'dateCreated': '2024-07-10T15:00:49.626Z',
            'dateModified': '2024-07-10T16:02:36Z',
            'item': {
                '@type': 'PublicationIssue',
                'dateModified': '2024-07-10T16:02:36Z',
                'datePublished': '2024-07-10T15:00:49.626Z',
                'hasPart': [
                    {
                        '@type': 'CreativeWork',
                        'hasPart': [
                            {
                                '@type': 'Article',
                                'associatedMedia': [
                                    {
                                        '@type': 'MediaObject',
                                        'contentSize': '5.7K',
                                        'contentUrl': 'https://storage.cloud.google.com/digitalabo-medien/4b7db5db-af0d-4975-838d-ef1fbe6c86c9.xml',
                                        'dateModified': '2024-07-07T19:38:50Z',
                                        'encodingFormat': 'text/xml',
                                        'name': '4b7db5db-af0d-4975-838d-ef1fbe6c86c9.xml',
                                        'url': 'https://media-delivery.zeit.de/4b7db5db-af0d-4975-838d-ef1fbe6c86c9.xml',
                                    }
                                ],
                                'dateModified': '2024-07-07T19:38:50Z',
                                'identifier': 1068953,
                            },
                            {
                                '@type': 'Article',
                                'abstract': (
                                    'Über die Notwendigkeit, ' + 'dass Helmut Schmidt wiederkehrt.'
                                ),
                                'articleSection': 'zeitmagazin',
                                'associatedMedia': [
                                    {
                                        '@type': 'MediaObject',
                                        'contentSize': '6.5M',
                                        'contentUrl': 'https://storage.cloud.google.com/digitalabo-medien/715e31fd-edaf-436a-a42e-30546ba35319.mp3',
                                        'dateModified': '2024-07-10T14:39:38Z',
                                        'duration': 'PT4M42S',
                                        'encodingFormat': 'audio/mpeg',
                                        'name': '715e31fd-edaf-436a-a42e-30546ba35319.mp3',
                                        'url': 'https://media-delivery.zeit.de/715e31fd-edaf-436a-a42e-30546ba35319.mp3',
                                    },
                                    {
                                        '@type': 'MediaObject',
                                        'contentSize': '6K',
                                        'contentUrl': 'https://storage.cloud.google.com/digitalabo-medien/7cf7fe6f-f8db-4f99-8edd-21177ac9a3a7.xml',
                                        'dateModified': '2024-07-07T19:38:32Z',
                                        'encodingFormat': 'text/xml',
                                        'name': '7cf7fe6f-f8db-4f99-8edd-21177ac9a3a7.xml',
                                        'url': 'https://media-delivery.zeit.de/7cf7fe6f-f8db-4f99-8edd-21177ac9a3a7.xml',
                                    },
                                ],
                                'author': [{'@type': 'Person', 'name': 'Harald Martenstein'}],
                                'dateModified': '2024-07-10T14:39:47Z',
                                'identifier': 1064677,
                                'name': 'Harald Martenstein',
                            },
                        ],
                    }
                ],
            },
        }
    ],
    'dateModified': '2025-07-09T17:11:28Z',
    'name': 'DIE ZEIT',
}

BROKEN_DATA = {
    'dataFeedElement': [
        {
            'item': {
                'hasPart': [
                    {
                        'hasPart': [
                            {
                                'abstract': 'Media with nothing',
                                'identifier': 1,
                                'associatedMedia': [
                                    {
                                        'encodingFormat': 'audio/mpeg',
                                    },
                                ],
                            },
                            {
                                'abstract': 'Media without URL',
                                'identifier': 2,
                                'associatedMedia': [
                                    {
                                        'duration': 'PT4M42S',
                                        'encodingFormat': 'audio/mpeg',
                                    },
                                ],
                            },
                            {
                                'abstract': 'Media without duration',
                                'identifier': 3,
                                'associatedMedia': [
                                    {
                                        'encodingFormat': 'audio/mpeg',
                                        'url': 'https://media-delivery.zeit.de/715e31fd-edaf-436a-a42e-30546ba35319.mp3',
                                    },
                                ],
                            },
                            {
                                'abstract': 'Complete media',
                                'identifier': 4,
                                'associatedMedia': [
                                    {
                                        'duration': 'PT4M42S',
                                        'encodingFormat': 'audio/mpeg',
                                        'url': 'https://media-delivery.zeit.de/715e31fd-edaf-436a-a42e-30546ba35319.mp3',
                                    },
                                ],
                            },
                            {
                                'abstract': 'Media with broken duration',
                                'identifier': 5,
                                'associatedMedia': [
                                    {
                                        'duration': '2500',
                                        'encodingFormat': 'audio/mpeg',
                                        'url': 'https://media-delivery.zeit.de/715e31fd-edaf-436a-a42e-30546ba35319.mp3',
                                    },
                                ],
                            },
                        ]
                    }
                ]
            }
        }
    ]
}

NO_VOLUME = {
    '@context': 'https://schema.org',
    '@type': 'DataFeed',
    'name': 'DIE ZEIT',
    'dateModified': '2025-07-30T15:00:00Z',
    'dataFeedElement': [],
}

NO_PARTS = {
    '@context': 'https://schema.org',
    '@type': 'DataFeed',
    'name': 'DIE ZEIT',
    'dateModified': '2025-07-30T15:00:00Z',
    'dataFeedElement': [
        {
            '@type': 'DataFeedItem',
            'dateCreated': '2025-07-02T15:00:25.592Z',
            'dateModified': '2025-07-16T08:25:12Z',
            'item': {
                '@type': 'PublicationIssue',
                'dateModified': '2025-07-16T08:25:12Z',
                'datePublished': '2025-07-02T15:00:25.592Z',
                'issueNumber': 28,
                'isPartOf': {'@type': 'PublicationVolume', 'volumeNumber': 2025},
            },
        }
    ],
}


class TestImportAudios(zeit.mediaservice.testing.FunctionalTestCase):
    def test_get_audio_infos(self):
        mocker = requests_mock.Mocker()
        mocker.get('https://medien.zeit.de/feeds/die-zeit/issue?year=2025&number=1', json=DATA)
        with mocker:
            mediaservice = zeit.mediaservice.connection.Connection(
                'https://medien.zeit.de/feeds/die-zeit/issue'
            )
            audios = mediaservice.get_audio_infos(year=2025, volume=1)
            assert audios == {
                1064677: {
                    'url': 'https://media-delivery.zeit.de/715e31fd-edaf-436a-a42e-30546ba35319.mp3',
                    'duration': 282,
                }
            }

    def test_ignores_invalid_entries(self):
        mocker = requests_mock.Mocker()
        mocker.get(
            'https://medien.zeit.de/feeds/die-zeit/issue?year=2025&number=11', json=BROKEN_DATA
        )
        with mocker:
            mediaservice = zeit.mediaservice.connection.Connection(
                'https://medien.zeit.de/feeds/die-zeit/issue'
            )
            audios = mediaservice.get_audio_infos(year=2025, volume=11)
            assert audios == {
                3: {
                    'url': 'https://media-delivery.zeit.de/715e31fd-edaf-436a-a42e-30546ba35319.mp3',
                    'duration': None,
                },
                4: {
                    'url': 'https://media-delivery.zeit.de/715e31fd-edaf-436a-a42e-30546ba35319.mp3',
                    'duration': 282,
                },
                5: {
                    'url': 'https://media-delivery.zeit.de/715e31fd-edaf-436a-a42e-30546ba35319.mp3',
                    'duration': None,
                },
            }

    def test_dont_fail_on_missing_volume(self):
        mocker = requests_mock.Mocker()
        mocker.get(
            'https://medien.zeit.de/feeds/die-zeit/issue?year=2025&number=500', json=NO_VOLUME
        )
        with mocker:
            mediaservice = zeit.mediaservice.connection.Connection(
                'https://medien.zeit.de/feeds/die-zeit/issue'
            )
            audios = mediaservice.get_audio_infos(year=2025, volume=500)
            assert not audios

    def test_dont_fail_on_volume_with_no_parts(self):
        mocker = requests_mock.Mocker()
        mocker.get('https://medien.zeit.de/feeds/die-zeit/issue?year=2025&number=28', json=NO_PARTS)
        with mocker:
            mediaservice = zeit.mediaservice.connection.Connection(
                'https://medien.zeit.de/feeds/die-zeit/issue'
            )
            audios = mediaservice.get_audio_infos(year=2025, volume=28)
            assert not audios
