# coding: utf8
import contextlib
import zeit.content.article.testing


class ImageTest(zeit.content.article.testing.FunctionalTestCase):

    def test_image_can_be_set(self):
        from zeit.content.article.edit.image import Image
        import lxml.objectify
        import zeit.cms.interfaces
        tree = lxml.objectify.E.tree(
            lxml.objectify.E.image())
        image = Image(None, tree.image)
        image.__name__ = u'myname'
        image.layout = u'large'
        image_uid = 'http://xml.zeit.de/2006/DSC00109_2.JPG'
        image.references = image.references.create(
            zeit.cms.interfaces.ICMSContent(image_uid))
        self.assertEqual(image_uid, image.references.target.uniqueId)
        self.assertEqual(image_uid, image.xml.get('src'))
        self.assertEqual(u'myname', image.__name__)
        self.assertEqual(u'large', image.layout)
        self.assertEllipsis("""\
<image ... src="{image_uid}" ... is_empty="False">
  <bu xsi:nil="true"/>
  <copyright py:pytype="str">&#169;</copyright>
</image>
        """.format(image_uid=image_uid), lxml.etree.tostring(
            image.xml, pretty_print=True))

    def test_setting_image_to_none_removes_href(self):
        from zeit.content.article.edit.image import Image
        import lxml.objectify
        tree = lxml.objectify.E.tree(
            lxml.objectify.E.image())
        image = Image(None, tree.image)
        image.xml.set('src', 'testid')
        image.references = None
        self.assertNotIn('href', image.xml.attrib)

    def get_image_article(self, content):
        from zeit.connector.resource import Resource
        import StringIO
        import zeit.cms.checkout.interfaces
        import zeit.cms.interfaces
        import zeit.connector.interfaces
        import zope.component
        article_xml = """
        <article xmlns:py="http://codespeak.net/lxml/objectify/pytype">
            <head/>
            <body>
              <division type="page">
                {0}
              </division>
            </body>
        </article>""".format(content)
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        connector.add(Resource(
            'http://xml.zeit.de/article', 'article', 'article',
            StringIO.StringIO(article_xml)))
        article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/article')
        return zeit.cms.checkout.interfaces.ICheckoutManager(
            article).checkout()

    def test_image_nodes_inside_p_are_migrated_on_checkout(self):
        article = self.get_image_article("""
                <p>A leading para</p>
                <p>Blarf<image src="myniceimage" /></p>
                                         """)
        self.assertEqual(
            ['p', 'image', 'p'],
            [el.tag for el in article.xml.body.division.iterchildren()])

    def test_empty_p_nodes_should_be_removed_on_image_migrate(self):
        article = self.get_image_article("""
                <p>A leading para</p>
                <p><image src="myniceimage" /></p>
                               """)
        self.assertEqual(
            ['p', 'image'],
            [el.tag for el in article.xml.body.division.iterchildren()])

    def test_image_tail_should_be_preserved_on_migrate(self):
        article = self.get_image_article("""
                <p>A leading para</p>
                <p><image src="myniceimage" /> a tail</p>
                               """)
        self.assertEqual(
            ['p', 'image', 'p'],
            [el.tag for el in article.xml.body.division.iterchildren()])
        self.assertEqual(
            ' a tail', article.xml.body.division.p[1].text)

    def test_image_should_be_moved_up_to_division_even_when_deeper_nested(
        self):
        article = self.get_image_article("""
                <p>A leading para</p>
                <p><strong> blah <image src="myniceimage" /></strong></p>
                               """)
        self.assertEqual(
            ['p', 'image', 'p'],
            [el.tag for el in article.xml.body.division.iterchildren()])

    def test_image_nodes_should_keep_reference_with_strange_chars_on_checkout(
        self):
        import zeit.connector.interfaces
        import zope.component
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        connector.move(u'http://xml.zeit.de/2006/DSC00109_2.JPG',
                       u'http://xml.zeit.de/2006/ÄÖÜ.JPG')
        article = self.get_image_article("""
                <p>A leading para</p>
                <image src="http://xml.zeit.de/2006/ÄÖÜ.JPG" />""")
        self.assertEqual(
            u'http://xml.zeit.de/2006/ÄÖÜ.JPG',
            article.xml.body.division.image.get('src'))

    def test_image_nodes_should_keep_reference_with_strange_chars_on_checkin(
        self):
        from zeit.content.article.interfaces import IArticle
        import zeit.cms.browser.form
        import zeit.cms.checkout.interfaces
        import zeit.cms.interfaces
        import zeit.connector.interfaces
        import zope.component
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        connector.move(u'http://xml.zeit.de/2006/DSC00109_2.JPG',
                       u'http://xml.zeit.de/2006/ÄÖÜ.JPG')
        article = self.get_image_article("""
                <p>A leading para</p>
                <image src="http://xml.zeit.de/2006/ÄÖÜ.JPG" />""")
        zeit.cms.browser.form.apply_default_values(article, IArticle)
        article.year = 2011
        article.title = u'title'
        article.ressort = u'Deutschland'
        wl = zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)
        article.keywords = (wl['testtag'], wl['testtag2'], wl['testtag3'],)
        article = zeit.cms.checkout.interfaces.ICheckinManager(
            article).checkin()
        self.assertEqual(
            u'http://xml.zeit.de/2006/ÄÖÜ.JPG',
            article.xml.body.division.image.get('src'))

    def test_image_referenced_via_IImages_is_copied_to_first_body_block(self):
        from zeit.content.article.edit.interfaces import IEditableBody
        from zeit.content.image.interfaces import IImages
        import zeit.cms.browser.form
        import zeit.cms.interfaces
        import zope.lifecycleevent

        self.repository['article'] = self.get_article()

        with zeit.cms.checkout.helper.checked_out(
            self.repository['article']) as co:
            body = IEditableBody(co)
            factory = zope.component.getAdapter(
                body, zeit.edit.interfaces.IElementFactory, 'image')
            image_block = factory()

            image_id = 'http://xml.zeit.de/2006/DSC00109_2.JPG'
            IImages(co).image = zeit.cms.interfaces.ICMSContent(image_id)
            zope.lifecycleevent.modified(
                co, zope.lifecycleevent.Attributes(IImages, 'image'))

            image_block = body.values()[0]
            self.assertEqual(image_id, image_block.references.target.uniqueId)
            self.assertFalse(image_block.is_empty)

            IImages(co).image = None
            zope.lifecycleevent.modified(
                co, zope.lifecycleevent.Attributes(IImages, 'image'))
            self.assertEqual(None, image_block.references)

    def test_IImages_is_not_copied_to_body_if_block_was_edited_manually(self):
        from zeit.content.article.edit.interfaces import IEditableBody
        from zeit.content.image.interfaces import IImages
        import zeit.cms.browser.form
        import zeit.cms.interfaces
        import zeit.content.image.testing
        import zope.lifecycleevent

        # XXX This test shouldn't be using image groups since they cannot be
        # referenced by image blocks anymore according to the IImage interface
        # spec. Leaving it as it was for the moment, though, as it still works
        # for proving the point of this test.
        image_group = zeit.content.image.testing.create_image_group()
        self.repository['article'] = self.get_article()
        with zeit.cms.checkout.helper.checked_out(
            self.repository['article']) as co:
            body = IEditableBody(co)
            factory = zope.component.getAdapter(
                body, zeit.edit.interfaces.IElementFactory, 'image')
            image_block = factory()
            image_block.references = image_block.references.create(
                image_group)
            image_block.set_manually = True

            image_id = 'http://xml.zeit.de/2006/DSC00109_2.JPG'
            IImages(co).image = zeit.cms.interfaces.ICMSContent(image_id)
            zope.lifecycleevent.modified(
                co, zope.lifecycleevent.Attributes(IImages, 'image'))

            image_block = body.values()[0]
            self.assertEqual(
                image_group.uniqueId, image_block.references.target.uniqueId)

    def test_image_block_retrieves_the_correct_xml_node(self):
        # The lxml.objectify API offer an insiduous source of bugs: Iterating
        # over a single element a) is possible and b) yields all siblings with
        # the same tag. So it has been easy for SingleReferenceProperty to
        # overlook the fact that when we find a single element via xpath,
        # that already is the one we want.
        from zeit.cms.interfaces import ICMSContent
        from zeit.content.article.edit.interfaces import IEditableBody
        import zope.component

        self.repository['article'] = self.get_article()

        with zeit.cms.checkout.helper.checked_out(
            self.repository['article']) as co:
            body = IEditableBody(co)
            factory = zope.component.getAdapter(
                body, zeit.edit.interfaces.IElementFactory, 'image')
            block = factory()
            block.references = block.references.create(ICMSContent(
                'http://xml.zeit.de/2006/DSC00109_2.JPG'))
            block = factory()
            block.references = block.references.create(ICMSContent(
                'http://xml.zeit.de/2006/DSC00109_3.JPG'))

            self.assertEqual(
                'http://xml.zeit.de/2006/DSC00109_3.JPG',
                block.references.target.uniqueId)

    def test_setting_same_image_again_keeps_it(self):
        from zeit.cms.interfaces import ICMSContent
        from zeit.content.article.edit.interfaces import IEditableBody
        import zope.component

        self.repository['article'] = self.get_article()
        with zeit.cms.checkout.helper.checked_out(
            self.repository['article']) as co:
            body = IEditableBody(co)
            factory = zope.component.getAdapter(
                body, zeit.edit.interfaces.IElementFactory, 'image')
            block = factory()
            image_id = 'http://xml.zeit.de/2006/DSC00109_2.JPG'
            block.references = block.references.create(
                ICMSContent(image_id))
            self.assertEqual(image_id, block.references.target.uniqueId)
            block.references = block.references.get(image_id)
            self.assertEqual(image_id, block.references.target.uniqueId)

    @contextlib.contextmanager
    def image(self):
        from zeit.cms.interfaces import ICMSContent
        import zeit.cms.browser.form
        import zeit.cms.checkout.helper
        import zeit.content.article.edit.body
        import zeit.edit.interfaces
        import zope.component
        self.repository['article'] = self.get_article()
        with zeit.cms.checkout.helper.checked_out(
            self.repository['article']) as article:
            body = zeit.content.article.edit.body.EditableBody(
                article, article.xml.body)
            factory = zope.component.getAdapter(
                body, zeit.edit.interfaces.IElementFactory, 'image')
            image = factory()
            image.references = image.references.create(
                ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG'))
            yield image


class TestFactory(zeit.content.article.testing.FunctionalTestCase):

    def test_factory_should_create_image_node(self):
        import zeit.content.article.article
        import zeit.content.article.edit.body
        import zeit.content.article.edit.interfaces
        import zeit.edit.interfaces
        import zope.component
        article = zeit.content.article.article.Article()
        body = zeit.content.article.edit.body.EditableBody(
            article, article.xml.body)
        factory = zope.component.getAdapter(
            body, zeit.edit.interfaces.IElementFactory, 'image')
        self.assertEqual('Image', factory.title)
        div = factory()
        self.assertTrue(
            zeit.content.article.edit.interfaces.IImage.providedBy(div))
        self.assertEqual('image', div.xml.tag)
