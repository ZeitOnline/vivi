import zeit.cms.testing
import zeit.workflow.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'dependency.txt',
        'syndication.txt',
        layer=zeit.workflow.testing.LAYER,
        package='zeit.workflow')
