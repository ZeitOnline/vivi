import zeit.content.cp.blocks
import zeit.content.cp.testing


def test_suite():
    return zeit.content.cp.testing.FunctionalDocFileSuite(
        'cpextra.txt',
        'teaser.txt',
        'xml.txt',
        package=zeit.content.cp.blocks,
    )
