import zope.interface.verify

import zeit.campus.testing


class TopicTest(zeit.campus.testing.FunctionalTestCase):
    def test_topic_should_adapt_content_properly(self):
        content = self.repository['testcontent']
        tplink = zeit.campus.interfaces.ITopic(content)
        zope.interface.verify.verifyObject(zeit.campus.interfaces.ITopic, tplink)
        zope.interface.verify.verifyObject(zeit.cms.content.interfaces.IXMLRepresentation, tplink)

    def test_topic_should_generate_proper_xml(self):
        content = self.repository['testcontent']
        refcp = self.repository['online']['2007']['01']['index']
        tplink = zeit.campus.interfaces.ITopic(content)
        tplink.page = refcp
        tplink.label = 'Moep'
        assert (
            len(
                tplink.xml.xpath(
                    ('//head/topic[' '@href="http://xml.zeit.de/online/2007/01/index"]')
                )
            )
            == 1
        )
        assert tplink.xml.xpath('//head/topic/label')[0].text == 'Moep'
