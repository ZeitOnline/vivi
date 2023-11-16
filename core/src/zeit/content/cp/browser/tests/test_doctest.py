import zeit.content.cp.testing


def test_suite():
    return zeit.content.cp.testing.FunctionalDocFileSuite(
        'README.txt',
        'landing.txt',
        'library.txt',
        'rule.txt',
        package='zeit.content.cp.browser',
        layer=zeit.content.cp.testing.WSGI_LAYER,
    )
