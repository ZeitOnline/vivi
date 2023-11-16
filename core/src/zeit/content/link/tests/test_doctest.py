import zeit.cms.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt', package='zeit.content.link', layer=zeit.content.link.testing.LAYER
    )
