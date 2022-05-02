# -*- coding: utf-8 -*-
import zeit.wochenende.interfaces
import zeit.wochenende.testing
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType


class SectionTest(zeit.wochenende.testing.FunctionalTestCase):

    def test_zwe_ressort_content_is_zwe_content(self):
        content = ExampleContentType()
        content.ressort = 'Wochenende'
        self.repository['zwecenterpage'] = content
        content = self.repository['zwecenterpage']
        self.assertTrue(zeit.wochenende.interfaces.IZWEContent.providedBy(
            content))
