# -*- coding: utf-8 -*-
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.zett.interfaces
import zeit.zett.testing


class SectionTest(zeit.zett.testing.FunctionalTestCase):
    def test_zett_ressort_content_is_ztt_content(self):
        content = ExampleContentType()
        content.ressort = 'zett'
        self.repository['zettartikel'] = content
        content = self.repository['zettartikel']
        self.assertTrue(zeit.zett.interfaces.IZTTContent.providedBy(content))
