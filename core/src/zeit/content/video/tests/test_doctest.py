import zeit.content.video.testing


def test_suite():
    return zeit.content.video.testing.FunctionalDocFileSuite(
        'asset.txt',
        'video.txt',
        package='zeit.content.video')
