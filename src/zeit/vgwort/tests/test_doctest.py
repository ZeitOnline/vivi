import zeit.vgwort.testing


def test_suite():
    return zeit.vgwort.testing.FunctionalDocFileSuite(
        'README.txt',
        package='zeit.vgwort')
