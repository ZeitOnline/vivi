# -*- coding: utf-8 -*-
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.arbeit.interfaces
import zeit.arbeit.testing


class SectionTest(zeit.arbeit.testing.FunctionalTestCase):
    def test_arbeit_ressort_content_is_zar_content(self):
        content = ExampleContentType()
        content.ressort = 'Arbeit'
        self.repository['arbeitartikel'] = content
        content = self.repository['arbeitartikel']
        self.assertTrue(zeit.arbeit.interfaces.IZARContent.providedBy(content))
