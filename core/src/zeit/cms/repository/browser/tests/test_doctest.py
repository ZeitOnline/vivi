import zeit.cms.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'delete.txt',
        'file.txt',
        'rename.txt',
        'tree.txt',
        package='zeit.cms.repository.browser',
    )
