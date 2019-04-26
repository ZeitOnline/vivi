import zeit.cms.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'feed.txt',
        'oldchannel.txt',
        package='zeit.cms.syndication'
    )
