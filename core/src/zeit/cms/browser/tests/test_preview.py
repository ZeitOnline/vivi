# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


class PreviewTest(zeit.cms.testing.FunctionalTestCase):

    def test_invalid_unique_ids_should_raise_valueerror(self):
        from zeit.cms.browser.preview import prefixed_url
        self.assertRaises(ValueError, prefixed_url, 'aprefix', 'foo')

    def test_adapting_cmscontent_should_return_preview_url(self):
        from zeit.cms.browser.interfaces import IPreviewURL
        import zope.component
        self.assertEqual(
            'http://localhost/preview-prefix/testcontent',
            zope.component.getMultiAdapter(
                (self.getRootFolder()['repository']['testcontent'], 'preview'),
                IPreviewURL))
