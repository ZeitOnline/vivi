import zeit.cms.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'contentmemo.txt',
        'dav.txt',
        'field.txt',
        'liveproperty.txt',
        'lxmlpickle.txt',
        'metadata.txt',
        'property.txt',
        package='zeit.cms.content',
    )
