import unittest
import zeit.cms.repository.interfaces
import zeit.cms.testcontenttype.testcontenttype
import zeit.cms.testing
import zeit.content.cp.testing
import zope.component


def create_content(root):
    with zeit.cms.testing.site(root):
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

        for i in range(3):
            name = 'c%s' % (i + 1)
            c = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
            c.teaserTitle = c.shortTeaserTitle = u'%s teaser' % name
            repository[name] = c


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zeit.content.cp.testing.FunctionalDocFileSuite(
        'av.txt',
        'cpextra.txt',
        'fullgraphical.txt',
        'teaser.txt',
        'teaser-countings.txt',
        'teaser-two-column-layout.txt',
        'xml.txt',
        package='zeit.content.cp.browser.blocks',
    ))
    rss_test = zeit.content.cp.testing.FunctionalDocFileSuite(
        'rss.txt',
        package='zeit.content.cp.browser.blocks',
        layer=zeit.content.cp.testing.FEED_SERVER_LAYER,
        globs=dict(layer=zeit.content.cp.testing.FEED_SERVER_LAYER))
    suite.addTest(rss_test)
    return suite
