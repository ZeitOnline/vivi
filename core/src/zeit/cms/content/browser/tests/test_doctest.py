import zeit.cms.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'template.txt',
        'typechange.txt',
        'widget.txt',
        'widget-subnav.txt',
        package='zeit.cms.content.browser')
