import unittest
import zeit.cms.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
        zeit.cms.testing.DocFileSuite('adapter.txt', 'property.txt', package='zeit.cms.content')
    )
    suite.addTest(
        zeit.cms.testing.FunctionalDocFileSuite(
            'contentmemo.txt',
            'contentuuid.txt',
            'dav.txt',
            'dublincore.txt',
            'field.txt',
            'liveproperty.txt',
            'lxmlpickle.txt',
            'metadata.txt',
            'sources.txt',
            'xmlsupport.txt',
            package='zeit.cms.content',
        )
    )
    return suite
